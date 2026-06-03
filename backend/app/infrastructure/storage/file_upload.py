from pathlib import Path

from fastapi import UploadFile

from app.config import Settings
from app.domain.exceptions import ValidationError

try:
    import magic
except ImportError:
    magic = None  # type: ignore[assignment]

_EXT_TO_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


async def read_validated_image(
    file: UploadFile,
    settings: Settings,
) -> tuple[bytes, str, str]:
    """Read upload, validate, return (bytes, content_type, extension)."""
    if not file.filename:
        raise ValidationError("Nome de arquivo inválido.")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_image_extensions:
        raise ValidationError(
            "Formato não permitido. Use JPG, JPEG, PNG ou WEBP."
        )

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise ValidationError(
            f"Arquivo excede o tamanho máximo de {settings.max_upload_size_mb}MB."
        )

    if file.content_type and file.content_type not in settings.allowed_image_mimes:
        raise ValidationError("Tipo MIME não permitido.")

    if magic is not None:
        detected = magic.from_buffer(content, mime=True)
        if detected not in settings.allowed_image_mimes:
            raise ValidationError("Conteúdo do arquivo não corresponde a uma imagem válida.")
        content_type = detected
    else:
        content_type = file.content_type or _EXT_TO_MIME.get(ext, "application/octet-stream")

    return content, content_type, ext


def delete_upload_file(url: str | None, settings: Settings) -> None:
    """Remove legacy files saved on disk before blob storage."""
    if not url or not url.startswith("/uploads/"):
        return
    relative = url.removeprefix("/uploads/")
    path = Path(settings.upload_dir) / relative
    if path.is_file():
        path.unlink()

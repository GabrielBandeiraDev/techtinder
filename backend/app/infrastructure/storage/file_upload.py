import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import Settings
from app.domain.exceptions import ValidationError

try:
    import magic
except ImportError:
    magic = None  # type: ignore[assignment]


async def validate_and_save_image(
    file: UploadFile,
    settings: Settings,
    subdirectory: str = "photos",
) -> str:
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

    upload_root = Path(settings.upload_dir) / subdirectory
    upload_root.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = upload_root / safe_name
    dest.write_bytes(content)

    return f"/uploads/{subdirectory}/{safe_name}"


def delete_upload_file(url: str | None, settings: Settings) -> None:
    if not url or not url.startswith("/uploads/"):
        return
    relative = url.removeprefix("/uploads/")
    path = Path(settings.upload_dir) / relative
    if path.is_file():
        path.unlink()

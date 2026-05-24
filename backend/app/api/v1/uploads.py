from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.dependencies import get_current_user
from app.core.exceptions import BadRequestException
from app.models.user import User
from app.schemas.common import APIResponse
from app.utils.file_storage import file_storage

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/product-image", status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        url = await file_storage.save_image(file)
    except ValueError as exc:
        raise BadRequestException(str(exc))
    return APIResponse(success=True, message="Product image uploaded", data={"url": url})


@router.post("/vendor-document", status_code=status.HTTP_201_CREATED)
async def upload_vendor_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        url = await file_storage.save_document(file)
    except ValueError as exc:
        raise BadRequestException(str(exc))
    return APIResponse(success=True, message="Vendor document uploaded", data={"url": url})

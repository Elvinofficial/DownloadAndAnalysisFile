from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.services import (
    get_calculation_service,
)
from app.api.schemas.calculations import (
    CalculationRequest,
    CalculationResponse,
    DigitStatistics,
    FileCalculationResponse,
)
from app.services.calculation_service import (
    CalculationFilesNotFoundError,
    CalculationService,
    InvalidFileContentError,
)


router = APIRouter(
    prefix="/calculations",
    tags=["Calculations"],
)


@router.post(
    "",
    response_model=CalculationResponse,
    status_code=status.HTTP_200_OK,
)
async def calculate_files(
    request: CalculationRequest,
    calculation_service: CalculationService = Depends(
        get_calculation_service,
    ),
) -> CalculationResponse:
    try:
        result = await calculation_service.calculate(
            file_ids=request.file_ids,
        )

    except CalculationFilesNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Some downloaded files were not found",
                "missing_file_ids": [
                    str(file_id)
                    for file_id in error.missing_file_ids
                ],
            },
        ) from error

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except InvalidFileContentError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return CalculationResponse(
        total=DigitStatistics(
            digits=result.total.digits,
            total_digits=result.total.total_digits,
        ),
        files=[
            FileCalculationResponse(
                file_id=file_result.file_id,
                file_name=file_result.file_name,
                statistics=DigitStatistics(
                    digits=file_result.statistics.digits,
                    total_digits=(
                        file_result.statistics.total_digits
                    ),
                ),
            )
            for file_result in result.files
        ],
    )
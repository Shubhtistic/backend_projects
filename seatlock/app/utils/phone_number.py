import phonenumbers
from phonenumbers import NumberParseException
from fastapi import HTTPException, status


def verify_mob_num(num: str) -> str:
    try:
        parsed_num = phonenumbers.parse(num)
        if not phonenumbers.is_valid_number(parsed_num):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Invalid Phone number",
            )
        return phonenumbers.format_number(
            parsed_num, phonenumbers.PhoneNumberFormat.E164
        )
    except NumberParseException:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Number: {num} could not be parsed (:",
        )

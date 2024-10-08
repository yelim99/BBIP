package com.bbip.global.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
@Getter
public class EncodingFailException extends RuntimeException {

    private static final int code = HttpStatus.INTERNAL_SERVER_ERROR.value();

    public EncodingFailException(String message) {
        super(message);
    }
}

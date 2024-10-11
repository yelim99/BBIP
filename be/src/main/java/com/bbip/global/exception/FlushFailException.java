package com.bbip.global.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
@Getter
public class FlushFailException extends RuntimeException {

    private static final int code = HttpStatus.INTERNAL_SERVER_ERROR.value();

    public FlushFailException(String message) {
        super(message);
    }
}

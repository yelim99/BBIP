package com.bbip.global.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.BAD_REQUEST)
@Getter
public class NotSameUserException extends RuntimeException {

    private static final int code = HttpStatus.BAD_REQUEST.value();

    public NotSameUserException(String message) {
        super(message);
    }
}

package com.bbip.global.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.NO_CONTENT)
@Getter
public class RtmpServerNotFoundException extends RuntimeException {

    private static final int code = HttpStatus.NO_CONTENT.value();

    public RtmpServerNotFoundException(String message) {
        super(message);
    }
}

package com.bbip.global.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
@Getter
public class VideoSaveFailException extends RuntimeException {

    private static final int code = HttpStatus.INTERNAL_SERVER_ERROR.value();

    public VideoSaveFailException(String message) {
        super(message);
    }
}

package com.bbip.global.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

/**
 * 받은 토큰이 유효하지 않은 경우 UNAUTHORIZED 401 반환
 *  401: 요청된 리소스에 대해 유효한 인증 자격 증명이 없기 때문에 클라이언트 요청이 완료되지 않았음을 나타냅니다.
 */
@ResponseStatus(HttpStatus.UNAUTHORIZED)
@Getter
public class InvalidTokenException extends RuntimeException {

    private static final int code = HttpStatus.UNAUTHORIZED.value();

    public InvalidTokenException(String message) {
        super(message);
    }
}

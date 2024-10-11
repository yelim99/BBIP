package com.bbip.global.response;

import lombok.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Slf4j
public class CommonResponse {

    HttpHeaders headers;
    HttpStatus status;
    String message;

    public CommonResponse(HttpHeaders headers, String message) {
        this.headers = headers;
        this.status = HttpStatus.OK;
        this.message = message;
    }

    public CommonResponse(String message) {
        this.status = HttpStatus.OK;
        this.message = message;
    }

//    /**
//     * 상태 번호의 코드네임을 반환하는 함수
//     * @return 상태 코드명
//     */
//    public HttpStatus getHttpStatus() {
//        try {
//            return HttpStatus.valueOf(statusCode);
//        } catch (IllegalArgumentException e) {
//            log.error("존재하지 않는 상태코드 반환 시도");
//            return HttpStatus.INTERNAL_SERVER_ERROR;
//        }
//    }

}

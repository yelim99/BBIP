package com.bbip.global.response;

import lombok.*;
import org.springframework.lang.Nullable;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class SingleResponse<T> extends CommonResponse {

    T data;

    @Builder
    public SingleResponse(String message, T data) {
        super(message);
        this.data = data;
    }
}

package com.bbip.global.response;

import lombok.*;
import org.springframework.lang.Nullable;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ListResponse<T> extends CommonResponse {

    List<T> dataList;

    @Builder
    public ListResponse(String message, List<T> dataList) {
        super(message);
        this.dataList = dataList;
    }
}

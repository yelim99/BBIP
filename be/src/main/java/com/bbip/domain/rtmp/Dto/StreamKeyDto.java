package com.bbip.domain.rtmp.Dto;

import lombok.*;
import org.springframework.stereotype.Component;

@Component
@Setter
@Getter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class StreamKeyDto {

    private Integer serverId;
    private String streamKey;

}

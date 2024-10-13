package com.bbip.domain.user.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ResponseUserDto {

    private Integer id;
    private String name;
    private String email;
    private String nickname;
    private String oauthProvider;
    private String imageUrl;

}

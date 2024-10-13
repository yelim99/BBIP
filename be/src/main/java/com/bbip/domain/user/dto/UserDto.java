package com.bbip.domain.user.dto;

import com.bbip.domain.user.entity.UserEntity;
import lombok.*;
import org.springframework.stereotype.Component;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Component
public class UserDto {

    private Integer id;
    private String name;
    private String email;
    private String nickname;
    private String oauthProvider;

    UserDto (String name, String email, String nickname, String oauthProvider) {
        this.name = name;
        this.email = email;
        this.nickname = nickname;
        this.oauthProvider = oauthProvider;
    }

    /**
     * Dto를 Entity로 변환하는 함수
     * @return 변환된 {@link UserEntity}
     */
    public UserEntity toEntity() {
        return UserEntity.builder()
                .id(id)
                .name(name)
                .email(email)
                .nickname(nickname)
                .oauthProvider(oauthProvider)
                .deleted(false)
                .build();
    }
}

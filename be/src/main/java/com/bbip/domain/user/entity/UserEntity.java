package com.bbip.domain.user.entity;

import com.bbip.domain.user.dto.UserDto;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.ColumnDefault;

@Entity
@Table(name = "user")
@Getter
@Setter
@NoArgsConstructor  // 기본 생성자 자동 생성
@AllArgsConstructor
@Builder
public class UserEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false, length = 255)  // 암호화된 이메일은 길이가 길어질 수 있으므로 길이 설정
    private String email;

    @Column(nullable = false, length = 20)
    private String name;

    @Column(nullable = false, length = 20)
    private String nickname;

    @Column(name = "oauth_provider", length = 100)
    private String oauthProvider;

    @Column(nullable = false)
    @ColumnDefault("0")
    private Boolean deleted;  // 소프트 삭제를 위한 필드

    /**
     * Entity를 Dto로 변환하는 함수
     * @return 변환된 {@link UserDto}
     */
    public UserDto toDto() {
        return UserDto.builder()
                .id(id)
                .name(name)
                .email(email)
                .nickname(nickname)
                .oauthProvider(oauthProvider)
                .build();
    }

    @Override
    public String toString() {
        return id + "-" + name + "[" + nickname + "] " + email;
    }

}
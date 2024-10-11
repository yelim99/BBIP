package com.bbip.domain.rtmp.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.*;

import java.io.Serializable;
import java.util.Objects;

@Embeddable
@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StreamKeyIdEntity implements Serializable {

    @Column(name = "user_id")
    private Integer userId;

    @Column(name = "server_id")
    private Integer serverId;

    // equals와 hashCode 메서드를 모두 재정의하여 동일성 판단(userId와 serverId가 모두 같아야 일치하는 객체임)

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof StreamKeyIdEntity)) return false;
        StreamKeyIdEntity that = (StreamKeyIdEntity) o;
        return Objects.equals(userId, that.userId) && Objects.equals(serverId, that.serverId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(userId, serverId);
    }
}

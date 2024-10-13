package com.bbip.domain.rtmp.entity;

import com.bbip.domain.user.entity.UserEntity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.ColumnDefault;

import java.io.Serializable;

@Entity
@Table(name = "stream_key")
@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StreamKeyEntity implements Serializable {

    @EmbeddedId
    private StreamKeyIdEntity id;

    @Column(name = "key", nullable = false, length = 100)
    private String key;

    @Column(nullable = false)
    @ColumnDefault("0")
    private Boolean stream;

    @ManyToOne(fetch = FetchType.LAZY)
    @MapsId("userId")
    @JoinColumn(name = "user_id", referencedColumnName = "id", foreignKey = @ForeignKey(name = "fk_streamkey_user"))
    private UserEntity userEntity;

    @ManyToOne(fetch = FetchType.LAZY)
    @MapsId("serverId")
    @JoinColumn(name = "server_id", referencedColumnName = "id", foreignKey = @ForeignKey(name = "fk_streamkey_server"))
    private RtmpServerEntity serverEntity;

}

package com.bbip.domain.rtmp.repository;

import com.bbip.domain.rtmp.entity.RtmpResult;
import com.bbip.domain.rtmp.entity.StreamKeyEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StreamKeyRepository extends JpaRepository<StreamKeyEntity, Integer> {

    @Query(value = """
    SELECT sk.userEntity.id AS userId, rs.id AS serverId, rs.name AS serverName, rs.uri AS serverUri, sk.key AS key, sk.stream AS stream
    FROM RtmpServerEntity rs
    JOIN StreamKeyEntity sk ON rs.id = sk.serverEntity.id
    WHERE sk.userEntity.id = :userId
    AND sk.stream = true
    """)
    List<RtmpResult> findStreamRtmpUrl(@Param("userId") Integer userId);

    @Query(value = """
    SELECT sk.userEntity.id AS userId, rs.id AS serverId, rs.name AS serverName, rs.uri AS serverUri, sk.key AS key, sk.stream AS stream
    FROM RtmpServerEntity rs
    JOIN StreamKeyEntity sk ON rs.id = sk.serverEntity.id
    WHERE sk.userEntity.id = :userId
    """)
    List<RtmpResult> findAllRtmpUrl(@Param("userId") Integer userId);

    @Modifying
    @Query(value = """
    DELETE FROM StreamKeyEntity sk 
    WHERE sk.userEntity.id = :userId AND sk.serverEntity.id = :serverId
    """)
    void deleteStreamKey(@Param("userId") Integer userId, @Param("serverId") Integer serverId);

    @Query(value = """
    SELECT sk FROM StreamKeyEntity sk WHERE sk.userEntity.id = :userId
    """)
    List<StreamKeyEntity> findAllStreamKey(int userId);

    @Modifying
    @Query(value = """
    UPDATE StreamKeyEntity sk SET sk.stream = :stream 
    WHERE sk.userEntity.id = :userId
    AND sk.serverEntity.id = :serverId
    """)
    void updateStreamKey(@Param("userId") Integer userId, @Param("serverId") Integer serverId, Boolean stream);
}

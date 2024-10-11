package com.bbip.domain.rtmp.repository;

import com.bbip.domain.rtmp.entity.RtmpServerEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface RtmpServerRepository extends JpaRepository<RtmpServerEntity, Integer> {

    Optional<RtmpServerEntity> findById(Integer id);
}

package com.bbip.domain.face.repository;

import com.bbip.domain.face.entity.FaceEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FaceRepository extends JpaRepository<FaceEntity, Integer> {

    @Query("SELECT f FROM FaceEntity f WHERE f.self = false AND f.userEntity.id = :userId")
    List<FaceEntity> findByUserId(int userId);

    @Query("SELECT f FROM FaceEntity f WHERE f.self = true AND f.userEntity.id = :userId")
    FaceEntity findMineById(int userId);

    @Query("SELECT f.fileName FROM FaceEntity f WHERE f.id = :id")
    String findFileNameById(int id);

}

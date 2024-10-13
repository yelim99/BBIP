package com.bbip.domain.user.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.bbip.domain.user.entity.UserEntity;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<UserEntity, Long> {

    @Query(value = """
    SELECT u FROM UserEntity u WHERE u.oauthProvider = :provider AND u.email = :email
    """)
    Optional<UserEntity> findUser(String email, String provider);

    UserEntity findById(int id);

    @Modifying
    @Query(value = """
    UPDATE UserEntity u SET u.deleted = true WHERE u.id = :id
    """)
    void signOut(int id);
}

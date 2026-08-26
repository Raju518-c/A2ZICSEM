/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.5.27-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: a2znewpython
-- ------------------------------------------------------
-- Server version	10.5.27-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_consent_record`
--

DROP TABLE IF EXISTS `accounts_consent_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_consent_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `consent_type` varchar(40) NOT NULL,
  `document_version` varchar(30) NOT NULL,
  `jurisdiction` varchar(20) NOT NULL,
  `is_granted` tinyint(1) NOT NULL,
  `granted_at` datetime(6) DEFAULT NULL,
  `withdrawn_at` datetime(6) DEFAULT NULL,
  `source` varchar(20) NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `user_agent` longtext NOT NULL,
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`metadata`)),
  `professional_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `accounts_consent_record_created_at_5fb06354` (`created_at`),
  KEY `accounts_consent_rec_professional_id_b7a2ae1c_fk_professio` (`professional_id`),
  KEY `accounts_consent_record_tenant_id_3dc36f78_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `accounts_consent_record_user_id_20a2aabd_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `accounts_consent_rec_professional_id_b7a2ae1c_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `accounts_consent_record_tenant_id_3dc36f78_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `accounts_consent_record_user_id_20a2aabd_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `chk_consent_record_granted_at_required` CHECK (`is_granted` = 0x00 or `granted_at` is not null),
  CONSTRAINT `chk_consent_record_withdrawn_after_granted` CHECK (`withdrawn_at` is null or `granted_at` is null or `withdrawn_at` > `granted_at`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_consent_record`
--

LOCK TABLES `accounts_consent_record` WRITE;
/*!40000 ALTER TABLE `accounts_consent_record` DISABLE KEYS */;
INSERT INTO `accounts_consent_record` VALUES (1,'2026-08-12 07:31:29.043513','TERMS','v1','IN',1,'2026-08-12 07:31:29.043150',NULL,'WEB',NULL,'','{}',1,1,3),(2,'2026-08-12 07:31:29.043584','PRIVACY','v1','IN',1,'2026-08-12 07:31:29.043250',NULL,'WEB',NULL,'','{}',1,1,3),(3,'2026-08-12 07:31:29.043633','RESUME_PROCESSING','v1','IN',1,'2026-08-12 07:31:29.043277',NULL,'WEB',NULL,'','{}',1,1,3),(4,'2026-08-12 07:31:29.043669','MARKETING','v1','IN',0,NULL,NULL,'WEB',NULL,'','{}',1,1,3),(5,'2026-08-14 06:29:11.967084','TERMS','v1','IN',1,'2026-08-14 06:29:11.966580',NULL,'WEB',NULL,'','{}',2,1,6),(6,'2026-08-14 06:29:11.967188','PRIVACY','v1','IN',1,'2026-08-14 06:29:11.966724',NULL,'WEB',NULL,'','{}',2,1,6),(7,'2026-08-14 06:29:11.967230','RESUME_PROCESSING','v1','IN',1,'2026-08-14 06:29:11.966751',NULL,'WEB',NULL,'','{}',2,1,6),(8,'2026-08-14 06:29:11.967263','MARKETING','v1','IN',0,NULL,NULL,'WEB',NULL,'','{}',2,1,6),(9,'2026-08-19 12:35:31.119005','PROFILE_ACCURACY','V1','',0,NULL,NULL,'WEB',NULL,'','{}',1,1,3),(10,'2026-08-19 12:35:31.151502','CONFLICT_OF_INTEREST','V1','',0,NULL,NULL,'WEB',NULL,'','{}',1,1,3),(11,'2026-08-19 12:35:41.078431','PROFILE_ACCURACY','V1','',1,'2026-08-19 12:35:41.319000',NULL,'WEB',NULL,'','{}',1,1,3),(12,'2026-08-19 12:35:41.085690','CONFLICT_OF_INTEREST','V1','',0,NULL,NULL,'WEB',NULL,'','{}',1,1,3),(13,'2026-08-19 12:37:23.030368','PROFILE_ACCURACY','V1','',1,'2026-08-19 12:37:23.271000',NULL,'WEB',NULL,'','{}',1,1,3),(14,'2026-08-19 12:37:23.039345','CONFLICT_OF_INTEREST','V1','',1,'2026-08-19 12:37:23.271000',NULL,'WEB',NULL,'','{}',1,1,3),(15,'2026-08-19 12:39:04.540053','PROFILE_ACCURACY','V1','',1,'2026-08-19 12:39:04.775000',NULL,'WEB',NULL,'','{}',1,1,3),(16,'2026-08-19 12:39:04.548172','CONFLICT_OF_INTEREST','V1','',1,'2026-08-19 12:39:04.775000',NULL,'WEB',NULL,'','{}',1,1,3),(17,'2026-08-19 12:42:38.106941','TERMS','v1','IN',1,'2026-08-19 12:42:38.106574',NULL,'WEB',NULL,'','{}',3,1,7),(18,'2026-08-19 12:42:38.107046','PRIVACY','v1','IN',1,'2026-08-19 12:42:38.106674',NULL,'WEB',NULL,'','{}',3,1,7),(19,'2026-08-19 12:42:38.107087','RESUME_PROCESSING','v1','IN',1,'2026-08-19 12:42:38.106697',NULL,'WEB',NULL,'','{}',3,1,7),(20,'2026-08-19 12:42:38.107134','MARKETING','v1','IN',0,NULL,NULL,'WEB',NULL,'','{}',3,1,7),(21,'2026-08-21 10:16:55.784631','PROFILE_ACCURACY','V1','',1,'2026-08-21 10:16:55.678000',NULL,'WEB',NULL,'','{}',2,1,6),(22,'2026-08-21 10:16:55.791368','CONFLICT_OF_INTEREST','V1','',1,'2026-08-21 10:16:55.678000',NULL,'WEB',NULL,'','{}',2,1,6);
/*!40000 ALTER TABLE `accounts_consent_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_otp_verification`
--

DROP TABLE IF EXISTS `accounts_otp_verification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_otp_verification` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `otp_type` varchar(30) NOT NULL,
  `otp` varchar(128) NOT NULL,
  `sent_to` varchar(254) NOT NULL,
  `expires_at` datetime(6) NOT NULL,
  `is_used` tinyint(1) NOT NULL,
  `attempts` smallint(5) unsigned NOT NULL CHECK (`attempts` >= 0),
  `created_at` datetime(6) NOT NULL,
  `tenant_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_otp_tenant_sent_type` (`tenant_id`,`sent_to`,`otp_type`,`is_used`),
  KEY `idx_otp_expires_at` (`expires_at`),
  CONSTRAINT `accounts_otp_verific_tenant_id_e686b81d_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_otp_expires_after_created` CHECK (`expires_at` > `created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_otp_verification`
--

LOCK TABLES `accounts_otp_verification` WRITE;
/*!40000 ALTER TABLE `accounts_otp_verification` DISABLE KEYS */;
INSERT INTO `accounts_otp_verification` VALUES (1,'EMAIL','pbkdf2_sha256$1000000$jD6xoP1rhHig6THu9u1FZE$LRNVpRpRvfwJMbR/xQxrH819DfAhgVXGyVfrpR34t+Q=','sharvanikokkonda@gmail.com','2026-08-12 07:39:32.059119',1,0,'2026-08-12 07:29:32.059773',1),(2,'EMAIL','pbkdf2_sha256$1000000$i9ujgm95MKe8Dz0XFM4A1r$VWPXPLWDSqNvlZthOhuhcHLb34sRtD2qIWNzZKqJhJY=','kokkondasharvani@gmail.com','2026-08-13 15:45:11.591386',1,0,'2026-08-13 15:35:11.592575',1),(3,'EMAIL','pbkdf2_sha256$1000000$GIZxmHGEzmKVy9hhJqrbin$K6rO3Qos32U1hnXF7qS90Thjxq6Zal27l5hf7yqCyfM=','sharvani6799@gmail.com','2026-08-13 15:46:07.121229',0,0,'2026-08-13 15:36:07.121654',1),(4,'EMAIL','pbkdf2_sha256$1000000$c6aTE1V76vXnITdPLakggl$hhUe5d8zPswujjT4ssAZEoth0saqbR+nVpODP05Q1UM=','sharvanikokkonda@gmail.com','2026-08-13 15:47:26.702111',1,0,'2026-08-13 15:37:26.702534',1),(5,'EMAIL','pbkdf2_sha256$1000000$ZsX6dqvnsipuTq584G72KQ$EFRKDlT6YVR+afpNGTqPZKIT/5MqWqAlFiMNFI8j2/g=','sharvanikokkonda@gmail.com','2026-08-14 06:21:35.283704',0,0,'2026-08-14 06:11:35.284680',1),(6,'EMAIL','pbkdf2_sha256$1000000$5RReGab1NwkfIgbj67OgvV$s8GpUQeH3XMbEv8fhm7k1fil+IfnJRRN8kyXt4pfYaA=','kokkondasharvani@gmail.com','2026-08-14 06:21:52.126407',0,0,'2026-08-14 06:11:52.126861',1),(7,'EMAIL','pbkdf2_sha256$1000000$EMdEwUV0U2Cgj7cWMXsJnS$kZyO0m7rRgcbPPOxO7erJM89C7+S36vUpdqy08gBSbQ=','pavanimyana2000@gmail.com','2026-08-14 06:34:25.019237',1,0,'2026-08-14 06:24:25.019659',1),(8,'EMAIL','pbkdf2_sha256$1000000$JzjhTzvWhsKad2AZUKzhiE$bIjGG0b6rjFiq7sERSsqAHLO79lKB2DhLSiVn6L0EX8=','pavanimyana2000@gmail.com','2026-08-14 06:36:31.728505',1,0,'2026-08-14 06:26:31.728937',1),(9,'EMAIL','pbkdf2_sha256$1000000$027gu5VB3u0KbHmDnxtT12$7eUmAhhgIa5rNf+Yp6ona7g8iaTuWuab6SREzoCGzJM=','myanapavani570@gmail.com','2026-08-14 06:40:51.652032',1,0,'2026-08-14 06:30:51.652432',1),(10,'EMAIL','pbkdf2_sha256$1000000$IpZMBfpqEBNyqxbkDf0iQK$qI2sC2MPyf4ik4UjR8k0yOtdK9AiXAbBzJyZWqKrFbo=','myanapavani570@gmail.com','2026-08-14 09:10:50.573877',1,0,'2026-08-14 09:00:50.574783',1),(11,'EMAIL','pbkdf2_sha256$1000000$asmzwUQeYwecvqtkVapkoA$42l07RY/SLAFhi/EyAcuLv1vaEzxxW2KXe/PuAMqXVo=','myanapavani570@gmail.com','2026-08-14 09:18:41.251456',1,0,'2026-08-14 09:08:41.251846',1),(12,'EMAIL','pbkdf2_sha256$1000000$2wBw65rptRPNkcYfhhzw5y$p7RUWEEV8OwYWpFFEjOmU1PEaUR7/iHe+LVEH/X0cbg=','myanapavani570@gmail.com','2026-08-14 12:19:10.344015',1,0,'2026-08-14 12:09:10.344549',1),(13,'EMAIL','pbkdf2_sha256$1000000$mQpnwwzUaA2iMTlYYggoKy$RaNFpVamDsPRmdepByj4V2HgfE5iRm/sHmQcNkLtKIY=','myanapavani570@gmail.com','2026-08-19 08:42:42.183928',1,0,'2026-08-19 08:32:42.184489',1),(14,'EMAIL','pbkdf2_sha256$1000000$zJkTCLNDXLRzn7kFOAoQDw$gxTjS5deTYS9wQyTFkO46upa9qObPKUnmZ3gsvgG2xM=','myanapavani570@gmail.com','2026-08-19 09:20:49.938924',0,0,'2026-08-19 09:10:49.939425',1),(15,'EMAIL','pbkdf2_sha256$1000000$xjtLWQ70aZV2Rq9bDJfMYf$qMTMumscXfUUh91qI7NxOwvqpEmbhsZJvXaJefg54IA=','rajushanigarapu1997@gmail.com','2026-08-19 12:48:00.870913',1,0,'2026-08-19 12:38:00.871437',1);
/*!40000 ALTER TABLE `accounts_otp_verification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_registration_application`
--

DROP TABLE IF EXISTS `accounts_registration_application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_registration_application` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `application_version` int(10) unsigned NOT NULL CHECK (`application_version` >= 0),
  `selected_operating_country` varchar(2) NOT NULL,
  `status` varchar(30) NOT NULL,
  `stage1_snapshot` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`stage1_snapshot`)),
  `submitted_at` datetime(6) DEFAULT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `decision_reason` longtext NOT NULL,
  `selected_industry_id` bigint(20) NOT NULL,
  `selected_scope_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  `decision_history` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`decision_history`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_registration_application_tenant_user_version` (`tenant_id`,`user_id`,`application_version`),
  KEY `accounts_registration_application_created_at_5ce95008` (`created_at`),
  KEY `accounts_registration_application_status_5f7607a1` (`status`),
  KEY `accounts_registratio_selected_industry_id_7a09d81c_fk_catalog_r` (`selected_industry_id`),
  KEY `accounts_registratio_selected_scope_id_5008a901_fk_catalog_s` (`selected_scope_id`),
  KEY `accounts_registratio_reviewed_by_id_abd967c4_fk_accounts_` (`reviewed_by_id`),
  KEY `accounts_registratio_user_id_87388375_fk_accounts_` (`user_id`),
  CONSTRAINT `accounts_registratio_reviewed_by_id_abd967c4_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `accounts_registratio_selected_industry_id_7a09d81c_fk_catalog_r` FOREIGN KEY (`selected_industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `accounts_registratio_selected_scope_id_5008a901_fk_catalog_s` FOREIGN KEY (`selected_scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `accounts_registratio_tenant_id_c1c18828_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `accounts_registratio_user_id_87388375_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `chk_registration_application_submitted_at_required` CHECK (`status` = 'DRAFT' or `submitted_at` is not null),
  CONSTRAINT `chk_registration_application_reviewed_at_required` CHECK (`status` not in ('APPROVED','REJECTED','RETURNED') or `reviewed_at` is not null),
  CONSTRAINT `chk_registration_application_decision_reason_required` CHECK (`status` not in ('REJECTED','RETURNED') or `decision_reason` <> '')
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_registration_application`
--

LOCK TABLES `accounts_registration_application` WRITE;
/*!40000 ALTER TABLE `accounts_registration_application` DISABLE KEYS */;
INSERT INTO `accounts_registration_application` VALUES (1,'04aa38602d594c60a75c7bbe3e3d2ec1','2026-08-12 07:31:29.022850','2026-08-12 07:43:25.599035',1,'IN','APPROVED','{\"tenant\": \"1\", \"email\": \"sharvanikokkonda@gmail.com\", \"mobile_country_code\": \"+91\", \"mobile_number\": \"7676565656\", \"password\": \"User@123\", \"mfa_method\": \"Authenticator\", \"referral_source\": \"\", \"referral_code\": \"\", \"first_name\": \"Sharvani\", \"middle_name\": \"\", \"last_name\": \"Kokkonda\", \"preferred_name\": \"\", \"name_display_order\": \"Given-Family\", \"country_of_residence\": \"IN\", \"city\": \"karimnagar\", \"time_zone\": \"Asia/Kolkata\", \"primary_industry\": \"4\", \"primary_scope\": \"14\", \"self_declared_career_stage\": \"Aspirant / Graduate\", \"current_job_title\": \"\", \"initial_experience_band\": \"1-3\", \"highest_qualification_level\": \"Master\", \"terms\": true, \"privacy\": true, \"resume_processing\": true, \"marketing\": false}','2026-08-12 07:31:29.022345','2026-08-12 07:43:25.598762','Fill stage 2 form',4,14,1,1,3,'[]'),(2,'7837abd61b2842439202b1fc0e3cd972','2026-08-14 06:29:11.909048','2026-08-19 08:30:28.970409',1,'IN','APPROVED','{\"tenant\": \"1\", \"email\": \"pavanimyana2000@gmail.com\", \"mobile_country_code\": \"+91\", \"mobile_number\": \"9676704365\", \"password\": \"Pavani@123\", \"mfa_method\": \"Email\", \"referral_source\": \"\", \"referral_code\": \"\", \"first_name\": \"Pavani\", \"middle_name\": \"\", \"last_name\": \"Myana\", \"preferred_name\": \"\", \"name_display_order\": \"Family-Given\", \"country_of_residence\": \"IN\", \"city\": \"Sircilla\", \"time_zone\": \"Asia/Kolkata\", \"primary_industry\": \"1\", \"primary_scope\": \"1\", \"self_declared_career_stage\": \"Junior Surveyor\", \"current_job_title\": \"Junior Surveyor\", \"initial_experience_band\": \"1-3\", \"highest_qualification_level\": \"Degree\", \"terms\": true, \"privacy\": true, \"resume_processing\": true, \"marketing\": false}','2026-08-14 06:29:11.000000','2026-08-19 08:30:28.969862','',1,1,1,1,6,'[]'),(3,'2ba0d9f72d5b4e978625371a329e455a','2026-08-19 12:42:38.071420','2026-08-20 08:53:42.324335',1,'IN','APPROVED','{\"tenant\": \"1\", \"email\": \"rajushanigarapu1997@gmail.com\", \"mobile_country_code\": \"+91\", \"mobile_number\": \"9177951459\", \"password\": \"R@juraju1234\", \"mfa_method\": \"Email\", \"referral_source\": \"\", \"referral_code\": \"\", \"first_name\": \"Raju\", \"middle_name\": \"\", \"last_name\": \"Shanigarapu\", \"preferred_name\": \"\", \"name_display_order\": \"Family-Given\", \"country_of_residence\": \"IN\", \"city\": \"Hyderabad\", \"time_zone\": \"Asia/Kolkata\", \"primary_industry\": \"1\", \"primary_scope\": \"1\", \"self_declared_career_stage\": \"Junior Surveyor\", \"current_job_title\": \"\", \"initial_experience_band\": \"1-3\", \"highest_qualification_level\": \"Master\", \"terms\": true, \"privacy\": true, \"resume_processing\": true, \"marketing\": false}','2026-08-19 12:42:38.070710','2026-08-20 08:53:42.323932','',1,1,1,1,7,'[]');
/*!40000 ALTER TABLE `accounts_registration_application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_roles`
--

DROP TABLE IF EXISTS `accounts_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_roles` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `code` varchar(16) NOT NULL,
  `name` varchar(32) NOT NULL,
  `roles_for` varchar(16) NOT NULL,
  `created` datetime(6) NOT NULL,
  `tenant_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `accounts_roles_tenant_id_0511d66e_fk_tenancy_tenant_id` (`tenant_id`),
  CONSTRAINT `accounts_roles_tenant_id_0511d66e_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_roles`
--

LOCK TABLES `accounts_roles` WRITE;
/*!40000 ALTER TABLE `accounts_roles` DISABLE KEYS */;
INSERT INTO `accounts_roles` VALUES (1,'5000','Super Admin','super admin','2026-08-12 06:27:39.597860',NULL),(2,'88293','Admin','super admin','2026-08-12 07:06:56.936947',1),(4,'MGR','Manager','super admin','2026-08-13 04:54:49.893674',NULL);
/*!40000 ALTER TABLE `accounts_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user`
--

DROP TABLE IF EXISTS `accounts_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `email` varchar(254) NOT NULL,
  `mobile_country_code` varchar(5) NOT NULL,
  `mobile_number` varchar(15) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_candidate` tinyint(1) NOT NULL,
  `is_mentor` tinyint(1) NOT NULL,
  `approval_status` varchar(30) NOT NULL,
  `email_verified_at` datetime(6) DEFAULT NULL,
  `mobile_verified_at` datetime(6) DEFAULT NULL,
  `mfa_method` varchar(20) NOT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `rejection_reason` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `failed_login_attempts` smallint(5) unsigned NOT NULL CHECK (`failed_login_attempts` >= 0),
  `locked_until` datetime(6) DEFAULT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `date_joined` datetime(6) NOT NULL,
  `referral_source` varchar(100) DEFAULT NULL,
  `referral_code` varchar(100) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `approved_by_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_user_tenant_mobile` (`tenant_id`,`mobile_country_code`,`mobile_number`),
  KEY `accounts_user_approval_status_0670d9cc` (`approval_status`),
  KEY `accounts_user_approved_by_id_26a274e7_fk_accounts_user_id` (`approved_by_id`),
  CONSTRAINT `accounts_user_approved_by_id_26a274e7_fk_accounts_user_id` FOREIGN KEY (`approved_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `accounts_user_tenant_id_1906c0a8_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_user_approved_at_required_when_approved` CHECK (`approval_status` <> 'APPROVED' or `approved_at` is not null),
  CONSTRAINT `chk_user_rejection_reason_required_when_rejected` CHECK (`approval_status` <> 'REJECTED' or `rejection_reason` <> '')
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user`
--

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` VALUES (1,'169e2d2b035044138e5fb900cffa8025','superadmin@gmail.com','+91','8374827384','pbkdf2_sha256$1000000$QljXH0cK6kmIMSg0ox4vwT$9tJLKSJxVfFJJOtljTUx8omTY9GozKnRSdWnjC/nfiM=',0,0,'APPROVED',NULL,NULL,'EMAIL','2026-08-12 06:48:10.000000','',1,0,0,0,NULL,'2026-08-25 10:41:55.127687','2026-08-12 06:48:17.088233',NULL,NULL,'2026-08-25 10:41:55.128036',NULL,NULL),(2,'15853b62b21047b0b749b7b8690cc983','admin@gmail.com','+91','9374827384','pbkdf2_sha256$1000000$SB6hyDuzqbYVHxLTrkCPt8$KKNs9sSyw1zGDi3JaAISnS3O8vl0jYP93e7tb5zamr0=',0,0,'APPROVED',NULL,NULL,'EMAIL','2026-08-12 07:08:21.000000','',1,0,0,0,NULL,'2026-08-25 12:30:56.856155','2026-08-12 07:08:33.313143',NULL,NULL,'2026-08-25 12:30:56.856361',NULL,1),(3,'54fd445da1974a1c938fda0ce31af001','sharvanikokkonda@gmail.com','+91','7676565656','pbkdf2_sha256$1000000$nogbO0ivPHyVvI8lAb5OvG$Wl89VbxagdB68g7zUpt2+bfhCMilIdvTp/aKKAwwmWM=',0,0,'APPROVED','2026-08-13 15:37:44.079809',NULL,'AUTHENTICATOR','2026-08-20 12:56:56.294402','',1,0,0,0,NULL,'2026-08-22 05:29:51.457408','2026-08-12 07:31:29.010687',NULL,NULL,'2026-08-22 05:29:51.457705',2,1),(5,'4b88ce44bcb34741a4368061f833e5bb','siri@gmail.com','+91','8247685019','pbkdf2_sha256$1000000$g5St3M6h8joOqMoapKgWbn$HDS65jJ4o+eXdeZvcPlefJMpJw509KSMBjFMR8D0ZEI=',0,0,'PENDING_APPROVAL',NULL,NULL,'EMAIL',NULL,'',1,0,0,0,NULL,NULL,'2026-08-13 06:34:03.962131',NULL,NULL,'2026-08-13 06:34:03.962168',1,NULL),(6,'2926c7f0357e404391fac0530bb6dcd5','pavanimyana2000@gmail.com','+91','9676704365','pbkdf2_sha256$1000000$ynkwBd2Zcrbw6dBtGQRh3U$FZol6rxPq6skOyjIqfa9bZIRe4vmn9ZMb3k/aAuA6mE=',0,0,'PENDING_APPROVAL',NULL,NULL,'EMAIL',NULL,'',1,0,0,0,NULL,'2026-08-25 08:34:49.986760','2026-08-14 06:29:11.884335',NULL,NULL,'2026-08-25 08:34:49.987051',NULL,1),(7,'ce18fc6dbbda4f529bbd3b429cc291fe','rajushanigarapu1997@gmail.com','+91','9177951459','pbkdf2_sha256$1000000$j44eqFy15tnHTVsmkeKvHP$4qtxnHSPsHZAbwdAc9liHZSWGXqSJFTu5IFp5Ua2+M4=',0,0,'PENDING_APPROVAL',NULL,NULL,'EMAIL',NULL,'',1,0,0,0,NULL,'2026-08-25 10:52:42.509868','2026-08-19 12:42:38.029443',NULL,NULL,'2026-08-25 10:52:42.510093',NULL,1);
/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_role`
--

DROP TABLE IF EXISTS `accounts_user_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_user_role` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `usertbl_id` bigint(20) NOT NULL,
  `roles_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_role_usertbl_id_roles_id_09ae9ae3_uniq` (`usertbl_id`,`roles_id`),
  KEY `accounts_user_role_roles_id_f11f58b7_fk_accounts_roles_id` (`roles_id`),
  CONSTRAINT `accounts_user_role_roles_id_f11f58b7_fk_accounts_roles_id` FOREIGN KEY (`roles_id`) REFERENCES `accounts_roles` (`id`),
  CONSTRAINT `accounts_user_role_usertbl_id_75170d43_fk_accounts_user_id` FOREIGN KEY (`usertbl_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_role`
--

LOCK TABLES `accounts_user_role` WRITE;
/*!40000 ALTER TABLE `accounts_user_role` DISABLE KEYS */;
INSERT INTO `accounts_user_role` VALUES (1,1,1),(2,2,2),(4,5,2);
/*!40000 ALTER TABLE `accounts_user_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=361 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add blacklisted token',7,'add_blacklistedtoken'),(26,'Can change blacklisted token',7,'change_blacklistedtoken'),(27,'Can delete blacklisted token',7,'delete_blacklistedtoken'),(28,'Can view blacklisted token',7,'view_blacklistedtoken'),(29,'Can add outstanding token',8,'add_outstandingtoken'),(30,'Can change outstanding token',8,'change_outstandingtoken'),(31,'Can delete outstanding token',8,'delete_outstandingtoken'),(32,'Can view outstanding token',8,'view_outstandingtoken'),(33,'Can add Tenant',9,'add_tenant'),(34,'Can change Tenant',9,'change_tenant'),(35,'Can delete Tenant',9,'delete_tenant'),(36,'Can view Tenant',9,'view_tenant'),(37,'Can add Organization',10,'add_organization'),(38,'Can change Organization',10,'change_organization'),(39,'Can delete Organization',10,'delete_organization'),(40,'Can view Organization',10,'view_organization'),(41,'Can add Tenant Operation',11,'add_tenantoperation'),(42,'Can change Tenant Operation',11,'change_tenantoperation'),(43,'Can delete Tenant Operation',11,'delete_tenantoperation'),(44,'Can view Tenant Operation',11,'view_tenantoperation'),(45,'Can add Consent Record',12,'add_consentrecord'),(46,'Can change Consent Record',12,'change_consentrecord'),(47,'Can delete Consent Record',12,'delete_consentrecord'),(48,'Can view Consent Record',12,'view_consentrecord'),(49,'Can add OTP Verification',13,'add_otpverification'),(50,'Can change OTP Verification',13,'change_otpverification'),(51,'Can delete OTP Verification',13,'delete_otpverification'),(52,'Can view OTP Verification',13,'view_otpverification'),(53,'Can add Registration Application',14,'add_registrationapplication'),(54,'Can change Registration Application',14,'change_registrationapplication'),(55,'Can delete Registration Application',14,'delete_registrationapplication'),(56,'Can view Registration Application',14,'view_registrationapplication'),(57,'Can add roles',15,'add_roles'),(58,'Can change roles',15,'change_roles'),(59,'Can delete roles',15,'delete_roles'),(60,'Can view roles',15,'view_roles'),(61,'Can add User',16,'add_usertbl'),(62,'Can change User',16,'change_usertbl'),(63,'Can delete User',16,'delete_usertbl'),(64,'Can view User',16,'view_usertbl'),(65,'Can add Credential Record',17,'add_credentialrecord'),(66,'Can change Credential Record',17,'change_credentialrecord'),(67,'Can delete Credential Record',17,'delete_credentialrecord'),(68,'Can view Credential Record',17,'view_credentialrecord'),(69,'Can add credential record item',18,'add_credentialrecorditem'),(70,'Can change credential record item',18,'change_credentialrecorditem'),(71,'Can delete credential record item',18,'delete_credentialrecorditem'),(72,'Can view credential record item',18,'view_credentialrecorditem'),(73,'Can add Professional Profile',19,'add_professionalprofile'),(74,'Can change Professional Profile',19,'change_professionalprofile'),(75,'Can delete Professional Profile',19,'delete_professionalprofile'),(76,'Can view Professional Profile',19,'view_professionalprofile'),(77,'Can add Contact Record',20,'add_contactrecord'),(78,'Can change Contact Record',20,'change_contactrecord'),(79,'Can delete Contact Record',20,'delete_contactrecord'),(80,'Can view Contact Record',20,'view_contactrecord'),(81,'Can add Capability Record',21,'add_capabilityrecord'),(82,'Can change Capability Record',21,'change_capabilityrecord'),(83,'Can delete Capability Record',21,'delete_capabilityrecord'),(84,'Can view Capability Record',21,'view_capabilityrecord'),(85,'Can add Professional Review',22,'add_professionalreview'),(86,'Can change Professional Review',22,'change_professionalreview'),(87,'Can delete Professional Review',22,'delete_professionalreview'),(88,'Can view Professional Review',22,'view_professionalreview'),(89,'Can add referencevalueoption set',23,'add_referencevalueoptionset'),(90,'Can change referencevalueoption set',23,'change_referencevalueoptionset'),(91,'Can delete referencevalueoption set',23,'delete_referencevalueoptionset'),(92,'Can view referencevalueoption set',23,'view_referencevalueoptionset'),(93,'Can add Form Module',24,'add_formmodule'),(94,'Can change Form Module',24,'change_formmodule'),(95,'Can delete Form Module',24,'delete_formmodule'),(96,'Can view Form Module',24,'view_formmodule'),(97,'Can add Form Field',25,'add_formfield'),(98,'Can change Form Field',25,'change_formfield'),(99,'Can delete Form Field',25,'delete_formfield'),(100,'Can view Form Field',25,'view_formfield'),(101,'Can add Reference Value',26,'add_referencevalue'),(102,'Can change Reference Value',26,'change_referencevalue'),(103,'Can delete Reference Value',26,'delete_referencevalue'),(104,'Can view Reference Value',26,'view_referencevalue'),(105,'Can add Scope Catalog',27,'add_scopecatalog'),(106,'Can change Scope Catalog',27,'change_scopecatalog'),(107,'Can delete Scope Catalog',27,'delete_scopecatalog'),(108,'Can view Scope Catalog',27,'view_scopecatalog'),(109,'Can add Scope Module',28,'add_scopemodule'),(110,'Can change Scope Module',28,'change_scopemodule'),(111,'Can delete Scope Module',28,'delete_scopemodule'),(112,'Can view Scope Module',28,'view_scopemodule'),(113,'Can add Exposure Log',29,'add_exposurelog'),(114,'Can change Exposure Log',29,'change_exposurelog'),(115,'Can delete Exposure Log',29,'delete_exposurelog'),(116,'Can view Exposure Log',29,'view_exposurelog'),(117,'Can add Professional Assignment',30,'add_professionalassignment'),(118,'Can change Professional Assignment',30,'change_professionalassignment'),(119,'Can delete Professional Assignment',30,'delete_professionalassignment'),(120,'Can view Professional Assignment',30,'view_professionalassignment'),(121,'Can add Project Record',31,'add_projectrecord'),(122,'Can change Project Record',31,'change_projectrecord'),(123,'Can delete Project Record',31,'delete_projectrecord'),(124,'Can view Project Record',31,'view_projectrecord'),(125,'Can add Project Scope',32,'add_projectscope'),(126,'Can change Project Scope',32,'change_projectscope'),(127,'Can delete Project Scope',32,'delete_projectscope'),(128,'Can view Project Scope',32,'view_projectscope'),(129,'Can add Scope Response',33,'add_scoperesponse'),(130,'Can change Scope Response',33,'change_scoperesponse'),(131,'Can delete Scope Response',33,'delete_scoperesponse'),(132,'Can view Scope Response',33,'view_scoperesponse'),(133,'Can add Employment Record',34,'add_employmentrecord'),(134,'Can change Employment Record',34,'change_employmentrecord'),(135,'Can delete Employment Record',34,'delete_employmentrecord'),(136,'Can view Employment Record',34,'view_employmentrecord'),(137,'Can add Evidence Document',35,'add_evidencedocument'),(138,'Can change Evidence Document',35,'change_evidencedocument'),(139,'Can delete Evidence Document',35,'delete_evidencedocument'),(140,'Can view Evidence Document',35,'view_evidencedocument'),(141,'Can add Competency Assessment',36,'add_competencyassessment'),(142,'Can change Competency Assessment',36,'change_competencyassessment'),(143,'Can delete Competency Assessment',36,'delete_competencyassessment'),(144,'Can view Competency Assessment',36,'view_competencyassessment'),(145,'Can add Professional Scope',37,'add_professionalscope'),(146,'Can change Professional Scope',37,'change_professionalscope'),(147,'Can delete Professional Scope',37,'delete_professionalscope'),(148,'Can view Professional Scope',37,'view_professionalscope'),(149,'Can add Resume Template',38,'add_resumetemplate'),(150,'Can change Resume Template',38,'change_resumetemplate'),(151,'Can delete Resume Template',38,'delete_resumetemplate'),(152,'Can view Resume Template',38,'view_resumetemplate'),(153,'Can add Resume Generation',39,'add_resumegeneration'),(154,'Can change Resume Generation',39,'change_resumegeneration'),(155,'Can delete Resume Generation',39,'delete_resumegeneration'),(156,'Can view Resume Generation',39,'view_resumegeneration'),(157,'Can add Audit Event',40,'add_auditevent'),(158,'Can change Audit Event',40,'change_auditevent'),(159,'Can delete Audit Event',40,'delete_auditevent'),(160,'Can view Audit Event',40,'view_auditevent'),(161,'Can add module',41,'add_module'),(162,'Can change module',41,'change_module'),(163,'Can delete module',41,'delete_module'),(164,'Can view module',41,'view_module'),(165,'Can add data export request',42,'add_dataexportrequest'),(166,'Can change data export request',42,'change_dataexportrequest'),(167,'Can delete data export request',42,'delete_dataexportrequest'),(168,'Can view data export request',42,'view_dataexportrequest'),(169,'Can add disclosure request',43,'add_disclosurerequest'),(170,'Can change disclosure request',43,'change_disclosurerequest'),(171,'Can delete disclosure request',43,'delete_disclosurerequest'),(172,'Can view disclosure request',43,'view_disclosurerequest'),(173,'Can add candidate consent',44,'add_candidateconsent'),(174,'Can change candidate consent',44,'change_candidateconsent'),(175,'Can delete candidate consent',44,'delete_candidateconsent'),(176,'Can view candidate consent',44,'view_candidateconsent'),(177,'Can add project',45,'add_project'),(178,'Can change project',45,'change_project'),(179,'Can delete project',45,'delete_project'),(180,'Can view project',45,'view_project'),(181,'Can add conflict of interest declaration',46,'add_conflictofinterestdeclaration'),(182,'Can change conflict of interest declaration',46,'change_conflictofinterestdeclaration'),(183,'Can delete conflict of interest declaration',46,'delete_conflictofinterestdeclaration'),(184,'Can view conflict of interest declaration',46,'view_conflictofinterestdeclaration'),(185,'Can add project placement',47,'add_projectplacement'),(186,'Can change project placement',47,'change_projectplacement'),(187,'Can delete project placement',47,'delete_projectplacement'),(188,'Can view project placement',47,'view_projectplacement'),(189,'Can add project requirement',48,'add_projectrequirement'),(190,'Can change project requirement',48,'change_projectrequirement'),(191,'Can delete project requirement',48,'delete_projectrequirement'),(192,'Can view project requirement',48,'view_projectrequirement'),(193,'Can add tenant approval matrix',49,'add_tenantapprovalmatrix'),(194,'Can change tenant approval matrix',49,'change_tenantapprovalmatrix'),(195,'Can delete tenant approval matrix',49,'delete_tenantapprovalmatrix'),(196,'Can view tenant approval matrix',49,'view_tenantapprovalmatrix'),(197,'Can add tenant branding',50,'add_tenantbranding'),(198,'Can change tenant branding',50,'change_tenantbranding'),(199,'Can delete tenant branding',50,'delete_tenantbranding'),(200,'Can view tenant branding',50,'view_tenantbranding'),(201,'Can add tenant business unit',51,'add_tenantbusinessunit'),(202,'Can change tenant business unit',51,'change_tenantbusinessunit'),(203,'Can delete tenant business unit',51,'delete_tenantbusinessunit'),(204,'Can view tenant business unit',51,'view_tenantbusinessunit'),(205,'Can add tenant contact',52,'add_tenantcontact'),(206,'Can change tenant contact',52,'change_tenantcontact'),(207,'Can delete tenant contact',52,'delete_tenantcontact'),(208,'Can view tenant contact',52,'view_tenantcontact'),(209,'Can add tenant document',53,'add_tenantdocument'),(210,'Can change tenant document',53,'change_tenantdocument'),(211,'Can delete tenant document',53,'delete_tenantdocument'),(212,'Can view tenant document',53,'view_tenantdocument'),(213,'Can add tenant authorised representative',54,'add_tenantauthorisedrepresentative'),(214,'Can change tenant authorised representative',54,'change_tenantauthorisedrepresentative'),(215,'Can delete tenant authorised representative',54,'delete_tenantauthorisedrepresentative'),(216,'Can view tenant authorised representative',54,'view_tenantauthorisedrepresentative'),(217,'Can add tenant integration',55,'add_tenantintegration'),(218,'Can change tenant integration',55,'change_tenantintegration'),(219,'Can delete tenant integration',55,'delete_tenantintegration'),(220,'Can view tenant integration',55,'view_tenantintegration'),(221,'Can add tenant invitation',56,'add_tenantinvitation'),(222,'Can change tenant invitation',56,'change_tenantinvitation'),(223,'Can delete tenant invitation',56,'delete_tenantinvitation'),(224,'Can view tenant invitation',56,'view_tenantinvitation'),(225,'Can add tenant legal acceptance',57,'add_tenantlegalacceptance'),(226,'Can change tenant legal acceptance',57,'change_tenantlegalacceptance'),(227,'Can delete tenant legal acceptance',57,'delete_tenantlegalacceptance'),(228,'Can view tenant legal acceptance',57,'view_tenantlegalacceptance'),(229,'Can add tenant legal entity',58,'add_tenantlegalentity'),(230,'Can change tenant legal entity',58,'change_tenantlegalentity'),(231,'Can delete tenant legal entity',58,'delete_tenantlegalentity'),(232,'Can view tenant legal entity',58,'view_tenantlegalentity'),(233,'Can add tenant billing',59,'add_tenantbilling'),(234,'Can change tenant billing',59,'change_tenantbilling'),(235,'Can delete tenant billing',59,'delete_tenantbilling'),(236,'Can view tenant billing',59,'view_tenantbilling'),(237,'Can add tenant legal settings',60,'add_tenantlegalsettings'),(238,'Can change tenant legal settings',60,'change_tenantlegalsettings'),(239,'Can delete tenant legal settings',60,'delete_tenantlegalsettings'),(240,'Can view tenant legal settings',60,'view_tenantlegalsettings'),(241,'Can add tenant location',61,'add_tenantlocation'),(242,'Can change tenant location',61,'change_tenantlocation'),(243,'Can delete tenant location',61,'delete_tenantlocation'),(244,'Can view tenant location',61,'view_tenantlocation'),(245,'Can add tenant membership',62,'add_tenantmembership'),(246,'Can change tenant membership',62,'change_tenantmembership'),(247,'Can delete tenant membership',62,'delete_tenantmembership'),(248,'Can view tenant membership',62,'view_tenantmembership'),(249,'Can add project membership',63,'add_projectmembership'),(250,'Can change project membership',63,'change_projectmembership'),(251,'Can delete project membership',63,'delete_projectmembership'),(252,'Can view project membership',63,'view_projectmembership'),(253,'Can add tenant module entitlement',64,'add_tenantmoduleentitlement'),(254,'Can change tenant module entitlement',64,'change_tenantmoduleentitlement'),(255,'Can delete tenant module entitlement',64,'delete_tenantmoduleentitlement'),(256,'Can view tenant module entitlement',64,'view_tenantmoduleentitlement'),(257,'Can add tenant nda',65,'add_tenantnda'),(258,'Can change tenant nda',65,'change_tenantnda'),(259,'Can delete tenant nda',65,'delete_tenantnda'),(260,'Can view tenant nda',65,'view_tenantnda'),(261,'Can add tenant notification settings',66,'add_tenantnotificationsettings'),(262,'Can change tenant notification settings',66,'change_tenantnotificationsettings'),(263,'Can delete tenant notification settings',66,'delete_tenantnotificationsettings'),(264,'Can view tenant notification settings',66,'view_tenantnotificationsettings'),(265,'Can add tenant numbering config',67,'add_tenantnumberingconfig'),(266,'Can change tenant numbering config',67,'change_tenantnumberingconfig'),(267,'Can delete tenant numbering config',67,'delete_tenantnumberingconfig'),(268,'Can view tenant numbering config',67,'view_tenantnumberingconfig'),(269,'Can add tenant operation log',68,'add_tenantoperationlog'),(270,'Can change tenant operation log',68,'change_tenantoperationlog'),(271,'Can delete tenant operation log',68,'delete_tenantoperationlog'),(272,'Can view tenant operation log',68,'view_tenantoperationlog'),(273,'Can add tenant report template',69,'add_tenantreporttemplate'),(274,'Can change tenant report template',69,'change_tenantreporttemplate'),(275,'Can delete tenant report template',69,'delete_tenantreporttemplate'),(276,'Can view tenant report template',69,'view_tenantreporttemplate'),(277,'Can add tenant resume template',70,'add_tenantresumetemplate'),(278,'Can change tenant resume template',70,'change_tenantresumetemplate'),(279,'Can delete tenant resume template',70,'delete_tenantresumetemplate'),(280,'Can view tenant resume template',70,'view_tenantresumetemplate'),(281,'Can add tenant role assignment',71,'add_tenantroleassignment'),(282,'Can change tenant role assignment',71,'change_tenantroleassignment'),(283,'Can delete tenant role assignment',71,'delete_tenantroleassignment'),(284,'Can view tenant role assignment',71,'view_tenantroleassignment'),(285,'Can add tenant scope',72,'add_tenantscope'),(286,'Can change tenant scope',72,'change_tenantscope'),(287,'Can delete tenant scope',72,'delete_tenantscope'),(288,'Can view tenant scope',72,'view_tenantscope'),(289,'Can add tenant security settings',73,'add_tenantsecuritysettings'),(290,'Can change tenant security settings',73,'change_tenantsecuritysettings'),(291,'Can delete tenant security settings',73,'delete_tenantsecuritysettings'),(292,'Can view tenant security settings',73,'view_tenantsecuritysettings'),(293,'Can add tenant ip restriction',74,'add_tenantiprestriction'),(294,'Can change tenant ip restriction',74,'change_tenantiprestriction'),(295,'Can delete tenant ip restriction',74,'delete_tenantiprestriction'),(296,'Can view tenant ip restriction',74,'view_tenantiprestriction'),(297,'Can add tenant settings',75,'add_tenantsettings'),(298,'Can change tenant settings',75,'change_tenantsettings'),(299,'Can delete tenant settings',75,'delete_tenantsettings'),(300,'Can view tenant settings',75,'view_tenantsettings'),(301,'Can add tenant subscription',76,'add_tenantsubscription'),(302,'Can change tenant subscription',76,'change_tenantsubscription'),(303,'Can delete tenant subscription',76,'delete_tenantsubscription'),(304,'Can view tenant subscription',76,'view_tenantsubscription'),(305,'Can add tenant tax registration',77,'add_tenanttaxregistration'),(306,'Can change tenant tax registration',77,'change_tenanttaxregistration'),(307,'Can delete tenant tax registration',77,'delete_tenanttaxregistration'),(308,'Can view tenant tax registration',77,'view_tenanttaxregistration'),(309,'Can add tenant terminology',78,'add_tenantterminology'),(310,'Can change tenant terminology',78,'change_tenantterminology'),(311,'Can delete tenant terminology',78,'delete_tenantterminology'),(312,'Can view tenant terminology',78,'view_tenantterminology'),(313,'Can add tenant verification',79,'add_tenantverification'),(314,'Can change tenant verification',79,'change_tenantverification'),(315,'Can delete tenant verification',79,'delete_tenantverification'),(316,'Can view tenant verification',79,'view_tenantverification'),(317,'Can add tenant workflow',80,'add_tenantworkflow'),(318,'Can change tenant workflow',80,'change_tenantworkflow'),(319,'Can delete tenant workflow',80,'delete_tenantworkflow'),(320,'Can view tenant workflow',80,'view_tenantworkflow'),(321,'Can add tenant workflow step',81,'add_tenantworkflowstep'),(322,'Can change tenant workflow step',81,'change_tenantworkflowstep'),(323,'Can delete tenant workflow step',81,'delete_tenantworkflowstep'),(324,'Can view tenant workflow step',81,'view_tenantworkflowstep'),(325,'Can add project candidate',82,'add_projectcandidate'),(326,'Can change project candidate',82,'change_projectcandidate'),(327,'Can delete project candidate',82,'delete_projectcandidate'),(328,'Can view project candidate',82,'view_projectcandidate'),(329,'Can add project requirement scope',83,'add_projectrequirementscope'),(330,'Can change project requirement scope',83,'change_projectrequirementscope'),(331,'Can delete project requirement scope',83,'delete_projectrequirementscope'),(332,'Can view project requirement scope',83,'view_projectrequirementscope'),(333,'Can add project scope link',84,'add_projectscopelink'),(334,'Can change project scope link',84,'change_projectscopelink'),(335,'Can delete project scope link',84,'delete_projectscopelink'),(336,'Can view project scope link',84,'view_projectscopelink'),(337,'Can add tenant domain',85,'add_tenantdomain'),(338,'Can change tenant domain',85,'change_tenantdomain'),(339,'Can delete tenant domain',85,'delete_tenantdomain'),(340,'Can view tenant domain',85,'view_tenantdomain'),(341,'Can add tenant industry',86,'add_tenantindustry'),(342,'Can change tenant industry',86,'change_tenantindustry'),(343,'Can delete tenant industry',86,'delete_tenantindustry'),(344,'Can view tenant industry',86,'view_tenantindustry'),(345,'Can add CalculatedFieldOverride',87,'add_calculatedfieldoverride'),(346,'Can change CalculatedFieldOverride',87,'change_calculatedfieldoverride'),(347,'Can delete CalculatedFieldOverride',87,'delete_calculatedfieldoverride'),(348,'Can view CalculatedFieldOverride',87,'view_calculatedfieldoverride'),(349,'Can add CalculatedFieldValueHistory',88,'add_calculatedfieldvaluehistory'),(350,'Can change CalculatedFieldValueHistory',88,'change_calculatedfieldvaluehistory'),(351,'Can delete CalculatedFieldValueHistory',88,'delete_calculatedfieldvaluehistory'),(352,'Can view CalculatedFieldValueHistory',88,'view_calculatedfieldvaluehistory'),(353,'Can add CalculationRuleSet',89,'add_calculationruleset'),(354,'Can change CalculationRuleSet',89,'change_calculationruleset'),(355,'Can delete CalculationRuleSet',89,'delete_calculationruleset'),(356,'Can view CalculationRuleSet',89,'view_calculationruleset'),(357,'Can add CalculationRule',90,'add_calculationrule'),(358,'Can change CalculationRule',90,'change_calculationrule'),(359,'Can delete CalculationRule',90,'delete_calculationrule'),(360,'Can view CalculationRule',90,'view_calculationrule');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$tBO0wSlSDlUZOZq1orXHcJ$wtGvKN6NY7cEZZytg2xfkWQnrXNt9cSAM+K9GtP5G6M=','2026-08-25 10:52:00.703443',1,'admin','','','',1,1,'2026-08-12 06:07:39.111769');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalog_form_field`
--

DROP TABLE IF EXISTS `catalog_form_field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalog_form_field` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `field_code` varchar(140) NOT NULL,
  `field_label` varchar(220) NOT NULL,
  `purpose` varchar(300) NOT NULL,
  `data_type` varchar(30) NOT NULL,
  `ui_control` varchar(50) NOT NULL,
  `is_required` tinyint(1) NOT NULL,
  `is_repeatable` tinyint(1) NOT NULL,
  `option_set` varchar(80) NOT NULL,
  `options_schema` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`options_schema`)),
  `validation_schema` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`validation_schema`)),
  `evidence_rule` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`evidence_rule`)),
  `resume_token` varchar(180) NOT NULL,
  `default_resume_visibility` varchar(30) NOT NULL,
  `data_classification` varchar(30) NOT NULL,
  `sequence` int(10) unsigned NOT NULL CHECK (`sequence` >= 0),
  `is_active` tinyint(1) NOT NULL,
  `created_by_id` bigint(20) NOT NULL,
  `form_module_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_form_field_module_code` (`form_module_id`,`field_code`),
  KEY `catalog_form_field_created_by_id_34948e05_fk_accounts_user_id` (`created_by_id`),
  KEY `catalog_form_field_created_at_6cebe045` (`created_at`),
  CONSTRAINT `catalog_form_field_created_by_id_34948e05_fk_accounts_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `catalog_form_field_form_module_id_b249e02a_fk_catalog_f` FOREIGN KEY (`form_module_id`) REFERENCES `catalog_form_module` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalog_form_field`
--

LOCK TABLES `catalog_form_field` WRITE;
/*!40000 ALTER TABLE `catalog_form_field` DISABLE KEYS */;
INSERT INTO `catalog_form_field` VALUES (1,'2026-08-12 08:09:36.143858','2026-08-12 08:09:36.143897','sm_bridge.bridge_heavy_structure_type','Bridge / heavy-structure type','Captures scope-specific experience','ENUM_LIST','Multi-select',1,0,'','[\"Steel girder\", \"truss\", \"cable-stayed\", \"suspension\", \"segmental\", \"launching gantry\", \"heavy module\"]','{}','{}','','OPTIONAL','PROFESSIONAL',0,1,1,1),(2,'2026-08-12 08:13:31.342151','2026-08-12 08:13:31.342183','sm_bridge.span_component_size_range','Span / component size range','Captures scope-specific experience','STRING','Text input',0,1,'','{}','{}','{}','','OPTIONAL','PROFESSIONAL',0,1,1,1),(3,'2026-08-12 08:14:25.347912','2026-08-12 08:14:25.347970','sm_bridge.critical_components_inspected','Critical components inspected','Captures scope-specific experience','ENUM','Select',1,0,'','[\"Girders\", \"trusses\", \"pylons\", \"bearings\", \"joints\", \"cables\", \"deck segments\"]','{}','{}','{{scope.sm_bridge.critical_components_inspected}}','OPTIONAL','PROFESSIONAL',0,1,1,1);
/*!40000 ALTER TABLE `catalog_form_field` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalog_form_module`
--

DROP TABLE IF EXISTS `catalog_form_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalog_form_module` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `module_code` varchar(40) NOT NULL,
  `module_name` varchar(180) NOT NULL,
  `version` int(10) unsigned NOT NULL CHECK (`version` >= 0),
  `description` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `published_at` datetime(6) DEFAULT NULL,
  `retired_at` datetime(6) DEFAULT NULL,
  `created_by_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_form_module_code_version` (`module_code`,`version`),
  KEY `catalog_form_module_created_by_id_efc6d038_fk_accounts_user_id` (`created_by_id`),
  KEY `catalog_form_module_created_at_f5072e9b` (`created_at`),
  KEY `catalog_form_module_status_c996a805` (`status`),
  CONSTRAINT `catalog_form_module_created_by_id_efc6d038_fk_accounts_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `chk_form_module_published_at_required` CHECK (`status` <> 'PUBLISHED' or `published_at` is not null),
  CONSTRAINT `chk_form_module_retired_at_required` CHECK (`status` <> 'RETIRED' or `retired_at` is not null)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalog_form_module`
--

LOCK TABLES `catalog_form_module` WRITE;
/*!40000 ALTER TABLE `catalog_form_module` DISABLE KEYS */;
INSERT INTO `catalog_form_module` VALUES (1,'2026-08-12 07:24:59.735172','2026-08-12 07:24:59.735196','SM-BRIDGE','SM-WELD',1,'','PUBLISHED',NULL,'2026-08-12 07:24:56.000000',NULL,1),(2,'2026-08-12 07:25:22.189862','2026-08-12 07:25:22.189898','SM-CIVIL','SM-CIVIL',1,'','PUBLISHED',NULL,'2026-08-12 07:25:17.000000',NULL,1),(3,'2026-08-12 07:25:38.895022','2026-08-12 07:25:38.895044','SM-COATING','SM-COATING',1,'','PUBLISHED',NULL,'2026-08-12 07:25:33.000000',NULL,1),(4,'2026-08-12 07:25:58.332515','2026-08-12 07:25:58.332545','SM-DIMENSIONAL','SM-DIMENSIONAL',1,'','PUBLISHED',NULL,'2026-08-12 07:25:53.000000',NULL,1),(5,'2026-08-12 07:26:14.932320','2026-08-12 07:26:14.932350','SM-FAT','SM-FAT',1,'','PUBLISHED',NULL,'2026-08-12 07:26:10.000000',NULL,1),(6,'2026-08-12 07:26:42.236845','2026-08-12 07:26:42.236877','SM-HULL','SM-HULL',1,'','PUBLISHED',NULL,'2026-08-12 07:26:37.000000',NULL,1),(7,'2026-08-12 07:26:58.446886','2026-08-12 07:26:58.446921','SM-LINEPIPE','SM-LINEPIPE',1,'','PUBLISHED',NULL,'2026-08-12 07:26:53.000000',NULL,1),(8,'2026-08-12 07:27:15.109343','2026-08-12 07:27:15.109374','SM-MEP','SM-MEP',1,'','PUBLISHED',NULL,'2026-08-12 07:27:10.000000',NULL,1),(9,'2026-08-12 07:27:36.960920','2026-08-12 07:27:36.960948','SM-MWS','SM-MWS',1,'','PUBLISHED',NULL,'2026-08-12 07:27:30.000000',NULL,1),(10,'2026-08-12 07:27:55.721344','2026-08-12 07:27:55.721367','SM-PACKING','SM-PACKING',1,'','PUBLISHED',NULL,'2026-08-12 07:27:50.000000',NULL,1),(11,'2026-08-12 07:28:14.909064','2026-08-12 07:28:14.909087','SM-PIPELINE','SM-PIPELINE',1,'','PUBLISHED',NULL,'2026-08-12 07:28:10.000000',NULL,1),(12,'2026-08-12 07:28:30.139717','2026-08-12 07:28:30.139737','SM-PRESSURE','SM-PRESSURE',1,'','PUBLISHED',NULL,'2026-08-12 07:28:25.000000',NULL,1),(13,'2026-08-12 07:29:30.088340','2026-08-12 07:29:30.088358','SM-ROPE','SM-ROPE',1,'','PUBLISHED',NULL,'2026-08-12 07:29:24.000000',NULL,1),(14,'2026-08-12 07:29:49.567704','2026-08-12 07:29:49.567729','SM-STRUCTSTEEL','SM-STRUCTSTEEL',1,'','PUBLISHED',NULL,'2026-08-12 07:29:44.000000',NULL,1),(15,'2026-08-12 07:30:09.185128','2026-08-12 07:30:09.185152','SM-SUBSEA','SM-SUBSEA',1,'','PUBLISHED',NULL,'2026-08-12 07:30:03.000000',NULL,1),(16,'2026-08-12 07:30:28.455430','2026-08-12 07:30:28.455475','SM-VENDOR','SM-VESSEL',1,'','PUBLISHED',NULL,'2026-08-12 07:30:22.000000',NULL,1),(17,'2026-08-12 07:30:46.148124','2026-08-12 07:30:46.148163','SM-WELD','SM-WELD',1,'','PUBLISHED',NULL,'2026-08-12 07:30:40.000000',NULL,1),(18,'2026-08-12 07:49:18.493966','2026-08-12 07:49:18.494013','SM-VESSEL','SM-VESSEL',1,'','PUBLISHED',NULL,'2026-08-12 07:49:13.000000',NULL,1);
/*!40000 ALTER TABLE `catalog_form_module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalog_reference_value`
--

DROP TABLE IF EXISTS `catalog_reference_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalog_reference_value` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `code` varchar(80) NOT NULL,
  `label` varchar(160) NOT NULL,
  `sort_order` smallint(5) unsigned NOT NULL CHECK (`sort_order` >= 0),
  `is_system` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`metadata`)),
  `created_by_id` bigint(20) NOT NULL,
  `parent_id` bigint(20) DEFAULT NULL,
  `option_set_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_reference_value_option_set_code` (`option_set_id`,`code`),
  KEY `catalog_reference_va_created_by_id_55631df3_fk_accounts_` (`created_by_id`),
  KEY `catalog_reference_va_parent_id_900df4f0_fk_catalog_r` (`parent_id`),
  KEY `catalog_reference_value_created_at_54742296` (`created_at`),
  CONSTRAINT `catalog_reference_va_created_by_id_55631df3_fk_accounts_` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `catalog_reference_va_option_set_id_abf3a205_fk_catalog_r` FOREIGN KEY (`option_set_id`) REFERENCES `catalog_referencevalueoptionset` (`id`),
  CONSTRAINT `catalog_reference_va_parent_id_900df4f0_fk_catalog_r` FOREIGN KEY (`parent_id`) REFERENCES `catalog_reference_value` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalog_reference_value`
--

LOCK TABLES `catalog_reference_value` WRITE;
/*!40000 ALTER TABLE `catalog_reference_value` DISABLE KEYS */;
INSERT INTO `catalog_reference_value` VALUES (1,'2026-08-12 06:53:39.019435','2026-08-12 06:54:18.880198','IN','Infrastructure',0,1,1,'{}',1,NULL,14),(2,'2026-08-12 06:54:35.678459','2026-08-12 06:54:35.678498','MF','Manufacturing',0,1,1,'{}',1,NULL,14),(3,'2026-08-12 06:54:51.903692','2026-08-12 06:54:51.903722','MO','Marine & Offshore',0,1,1,'{}',1,NULL,14),(4,'2026-08-12 06:55:06.078052','2026-08-12 06:55:06.078080','OG','Oil & Gas',0,1,1,'{}',1,NULL,14),(5,'2026-08-12 06:55:36.552190','2026-08-12 06:55:36.552224','1000','Aspirant / Graduate',0,1,1,'{}',1,NULL,13),(6,'2026-08-12 06:55:57.317756','2026-08-12 06:55:57.317788','1001','Independent Surveyor',0,1,1,'{}',1,NULL,13),(7,'2026-08-12 06:56:17.436774','2026-08-12 06:56:17.436795','1003','Junior Surveyor',0,1,1,'{}',1,NULL,13),(8,'2026-08-12 06:56:36.976237','2026-08-12 06:56:36.976260','1004','Principal / Technical Authority',0,1,1,'{}',1,NULL,13),(9,'2026-08-12 06:57:13.141022','2026-08-12 06:57:13.141052','1005','Senior / Lead / Validator',0,1,1,'{}',1,NULL,13),(10,'2026-08-12 06:57:34.034090','2026-08-12 06:57:34.034115','1006','Trainee Surveyor',0,1,1,'{}',1,NULL,13),(11,'2026-08-12 06:57:53.037889','2026-08-12 06:57:53.037912','PHOTOGRAPH','PHOTOGRAPH',0,1,1,'{}',1,NULL,6),(12,'2026-08-12 06:58:10.895828','2026-08-12 06:58:10.895850','RESUME','RESUME',0,1,1,'{}',1,NULL,6),(13,'2026-08-12 06:58:51.720690','2026-08-12 06:58:51.720725','2000','FIXED_TERM_CONTRACT',0,1,1,'{}',1,NULL,5),(14,'2026-08-12 06:59:10.015246','2026-08-12 06:59:10.015277','2001','PERMANENT',0,1,1,'{}',1,NULL,5),(15,'2026-08-12 06:59:24.600798','2026-08-12 06:59:24.600824','2002','PROJECT_BASED',0,1,1,'{}',1,NULL,5),(16,'2026-08-12 06:59:54.332815','2026-08-12 06:59:54.332839','3000','AUDITOR',0,1,1,'{}',1,NULL,4),(17,'2026-08-12 07:00:08.105905','2026-08-12 07:00:08.105936','3001','INSPECTOR',0,1,1,'{}',1,NULL,4),(18,'2026-08-12 07:00:24.305911','2026-08-12 07:00:24.305964','3002','SURVEYOR',0,1,1,'{}',1,NULL,4),(19,'2026-08-12 07:01:16.177847','2026-08-12 07:01:16.177879','4000','AVAILABLE_FROM_DATE',0,1,1,'{}',1,NULL,3),(20,'2026-08-12 07:01:34.839370','2026-08-12 07:01:34.839401','4001','AVAILABLE_IMMEDIATELY',0,1,1,'{}',1,NULL,3),(21,'2026-08-12 07:02:20.235622','2026-08-12 07:02:20.235651','4002','SERVING_NOTICE',0,1,1,'{}',1,NULL,3),(22,'2026-08-12 07:02:43.880228','2026-08-12 07:02:43.880254','4003','UNAVAILABLE',0,1,1,'{}',1,NULL,3),(23,'2026-08-12 07:03:18.572890','2026-08-12 07:03:18.572913','5000','DAILY',0,1,1,'{}',1,NULL,2),(24,'2026-08-12 07:03:33.432564','2026-08-12 07:03:33.432588','5001','HOURLY',0,1,1,'{}',1,NULL,2),(25,'2026-08-12 07:03:48.861786','2026-08-12 07:03:48.861807','5002','MONTHLY',0,1,1,'{}',1,NULL,2),(26,'2026-08-12 07:04:21.434401','2026-08-12 07:04:21.434429','6000','Female',0,1,1,'{}',1,NULL,1),(27,'2026-08-12 07:04:40.722127','2026-08-12 07:04:40.722160','6001','Male',0,1,1,'{}',1,NULL,1),(28,'2026-08-12 07:04:57.559281','2026-08-12 07:04:57.559310','6003','Other',0,1,1,'{}',1,NULL,1);
/*!40000 ALTER TABLE `catalog_reference_value` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalog_referencevalueoptionset`
--

DROP TABLE IF EXISTS `catalog_referencevalueoptionset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalog_referencevalueoptionset` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `option_type` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalog_referencevalueoptionset`
--

LOCK TABLES `catalog_referencevalueoptionset` WRITE;
/*!40000 ALTER TABLE `catalog_referencevalueoptionset` DISABLE KEYS */;
INSERT INTO `catalog_referencevalueoptionset` VALUES (1,'Gender'),(2,'Rate Type'),(3,'Availability Status'),(4,'Role Category'),(5,'Engagement Type'),(6,'EVIDENCE_TYPE'),(7,'SOFTWARE'),(8,'EQUIPMENT'),(9,'STANDARD'),(10,'PROFESSIONAL_ROLE'),(11,'QUALIFICATION_LEVEL'),(12,'AUTHORITY_STATUS'),(13,'QUALION_LEVEL'),(14,'INDUSTRY');
/*!40000 ALTER TABLE `catalog_referencevalueoptionset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalog_scope_catalog`
--

DROP TABLE IF EXISTS `catalog_scope_catalog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalog_scope_catalog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `code` varchar(40) NOT NULL,
  `scope_name` varchar(180) NOT NULL,
  `description` longtext NOT NULL,
  `competency_focus` longtext NOT NULL,
  `suggested_resume_section` varchar(160) NOT NULL,
  `activation_rule` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`activation_rule`)),
  `version` int(10) unsigned NOT NULL CHECK (`version` >= 0),
  `status` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_by_id` bigint(20) NOT NULL,
  `industry_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `catalog_scope_catalog_created_by_id_b50bec1f_fk_accounts_user_id` (`created_by_id`),
  KEY `catalog_scope_catalo_industry_id_5ae69601_fk_catalog_r` (`industry_id`),
  KEY `catalog_scope_catalog_created_at_17b855ca` (`created_at`),
  KEY `catalog_scope_catalog_status_e34e4ee5` (`status`),
  CONSTRAINT `catalog_scope_catalo_industry_id_5ae69601_fk_catalog_r` FOREIGN KEY (`industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `catalog_scope_catalog_created_by_id_b50bec1f_fk_accounts_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalog_scope_catalog`
--

LOCK TABLES `catalog_scope_catalog` WRITE;
/*!40000 ALTER TABLE `catalog_scope_catalog` DISABLE KEYS */;
INSERT INTO `catalog_scope_catalog` VALUES (1,'2026-08-12 07:17:51.256677','2026-08-12 07:17:51.256705','IN-BRIDGE','Bridges & Heavy Structures','Bridges & Heavy Structures','','','{}',1,'PUBLISHED',1,1,1),(2,'2026-08-12 07:18:16.643916','2026-08-12 07:18:16.643945','IN-CIVIL','Civil Works','Civil Works','','','{}',1,'PUBLISHED',1,1,1),(3,'2026-08-12 07:18:39.845074','2026-08-12 07:18:39.845103','IN-STEEL','Structural Steel','Structural Steel','','','{}',1,'PUBLISHED',1,1,1),(4,'2026-08-12 07:19:03.590142','2026-08-12 07:19:03.590179','MF-COAT','Coating & Finishing','Coating & Finishing','','','{}',1,'PUBLISHED',1,1,2),(5,'2026-08-12 07:19:24.217955','2026-08-12 07:19:24.217997','MF-DIM','Dimensional Inspection','','','','{}',1,'PUBLISHED',1,1,2),(6,'2026-08-12 07:19:44.428243','2026-08-12 07:19:44.428271','MF-FAT','Factory Acceptance Test','','','','{}',1,'PUBLISHED',1,1,2),(7,'2026-08-12 07:20:06.902269','2026-08-12 07:20:06.902295','MF-VENDOR','Vendor Inspection','','','','{}',1,'PUBLISHED',1,1,2),(8,'2026-08-12 07:20:31.522326','2026-08-12 07:20:31.522358','MF-WELD','Welding & Fabrication','','','','{}',1,'PUBLISHED',1,1,2),(9,'2026-08-12 07:20:51.514465','2026-08-12 07:20:51.514487','MO-HSM','Hull, Structure & Machinery','','','','{}',1,'PUBLISHED',1,1,3),(10,'2026-08-12 07:21:15.439444','2026-08-12 07:21:15.439482','MO-MWS','Marine Warranty Survey','','','','{}',1,'PUBLISHED',1,1,3),(11,'2026-08-12 07:21:37.674574','2026-08-12 07:21:37.674592','MO-VESSEL','Offshore Vessel Inspection','','','','{}',1,'PUBLISHED',1,1,3),(12,'2026-08-12 07:22:02.449124','2026-08-12 07:22:02.449160','MO-ROPE','Rope Access Inspection','','','','{}',1,'PUBLISHED',1,1,3),(13,'2026-08-12 07:22:24.696194','2026-08-12 07:22:24.696217','MO-SUBSEA','Subsea / Offshore Inspection Support','','','','{}',1,'PUBLISHED',1,1,3),(14,'2026-08-12 07:22:43.475524','2026-08-12 07:22:43.475548','OG-COAT','Coating & Corrosion','','','','{}',1,'PUBLISHED',1,1,4),(15,'2026-08-12 07:23:06.095785','2026-08-12 07:23:06.095820','OG-LPM','Line Pipe Manufacturing','','','','{}',1,'PUBLISHED',1,1,4),(16,'2026-08-12 07:23:30.335868','2026-08-12 07:23:30.335891','OG-PIPELINE','Pipeline Construction','','','','{}',1,'PUBLISHED',1,1,4),(17,'2026-08-12 07:23:49.314925','2026-08-12 07:23:49.314964','OG-PRESS','Pressure Equipment','','','','{}',1,'PUBLISHED',1,1,4),(18,'2026-08-12 07:24:09.603121','2026-08-12 07:24:09.603146','OG-WELD','Welding & Fabrication','','','','{}',1,'PUBLISHED',1,1,4);
/*!40000 ALTER TABLE `catalog_scope_catalog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalog_scope_module`
--

DROP TABLE IF EXISTS `catalog_scope_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalog_scope_module` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `sequence` smallint(5) unsigned NOT NULL CHECK (`sequence` >= 0),
  `is_required` tinyint(1) NOT NULL,
  `activation_rule` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`activation_rule`)),
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `created_by_id` bigint(20) NOT NULL,
  `form_module_id` bigint(20) NOT NULL,
  `scope_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_scope_module_scope_sequence` (`scope_id`,`sequence`),
  KEY `catalog_scope_module_created_by_id_6bcb3b50_fk_accounts_user_id` (`created_by_id`),
  KEY `catalog_scope_module_form_module_id_2b2e8036_fk_catalog_f` (`form_module_id`),
  KEY `catalog_scope_module_created_at_9a70f700` (`created_at`),
  CONSTRAINT `catalog_scope_module_created_by_id_6bcb3b50_fk_accounts_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `catalog_scope_module_form_module_id_2b2e8036_fk_catalog_f` FOREIGN KEY (`form_module_id`) REFERENCES `catalog_form_module` (`id`),
  CONSTRAINT `catalog_scope_module_scope_id_cf0bd317_fk_catalog_s` FOREIGN KEY (`scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `chk_scope_module_effective_from_before_to` CHECK (`effective_from` is null or `effective_to` is null or `effective_from` <= `effective_to`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalog_scope_module`
--

LOCK TABLES `catalog_scope_module` WRITE;
/*!40000 ALTER TABLE `catalog_scope_module` DISABLE KEYS */;
INSERT INTO `catalog_scope_module` VALUES (5,'2026-08-12 07:45:11.530194',0,1,'{}','2026-08-12',NULL,1,1,1),(6,'2026-08-12 07:46:10.527907',0,1,'{}',NULL,NULL,1,2,2),(7,'2026-08-12 07:46:27.121607',0,1,'{}',NULL,NULL,1,14,3),(8,'2026-08-12 07:46:40.679111',0,1,'{}',NULL,NULL,1,3,4),(9,'2026-08-12 07:46:54.428276',0,1,'{}',NULL,NULL,1,4,5),(10,'2026-08-12 07:47:09.758283',0,1,'{}',NULL,NULL,1,5,6),(11,'2026-08-12 07:47:24.123096',0,1,'{}',NULL,NULL,1,16,7),(12,'2026-08-12 07:47:38.483178',0,1,'{}',NULL,NULL,1,17,8),(13,'2026-08-12 07:47:57.351729',0,1,'{}',NULL,NULL,1,6,9),(14,'2026-08-12 07:48:11.213331',0,1,'{}',NULL,NULL,1,9,10),(15,'2026-08-12 07:56:29.155574',0,1,'{}',NULL,NULL,1,18,11),(16,'2026-08-12 07:56:41.045891',0,1,'{}',NULL,NULL,1,13,12),(17,'2026-08-12 07:56:54.126547',0,1,'{}',NULL,NULL,1,15,13),(18,'2026-08-12 08:00:35.132855',0,1,'{}',NULL,NULL,1,3,14),(19,'2026-08-12 08:06:32.126236',0,1,'{}',NULL,NULL,1,7,15),(20,'2026-08-12 08:07:21.291331',0,1,'{}',NULL,NULL,1,7,16),(21,'2026-08-12 08:07:36.205120',0,1,'{}',NULL,NULL,1,12,17),(22,'2026-08-12 08:07:47.233039',0,1,'{}',NULL,NULL,1,17,18);
/*!40000 ALTER TABLE `catalog_scope_module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `competency_assessment`
--

DROP TABLE IF EXISTS `competency_assessment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `competency_assessment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `assessment_type` varchar(30) NOT NULL,
  `assessor_role_snapshot` varchar(60) NOT NULL,
  `technical_knowledge_score` decimal(5,2) NOT NULL,
  `field_execution_score` decimal(5,2) NOT NULL,
  `documentation_evidence_score` decimal(5,2) NOT NULL,
  `ethics_independence_score` decimal(5,2) NOT NULL,
  `communication_conduct_score` decimal(5,2) NOT NULL,
  `recommendation` longtext NOT NULL,
  `decision` varchar(20) NOT NULL,
  `decision_reason` longtext NOT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `evidence_summary` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`evidence_summary`)),
  `assessed_at` datetime(6) NOT NULL,
  `approved_authority_id` bigint(20) DEFAULT NULL,
  `approved_by_id` bigint(20) DEFAULT NULL,
  `approved_level_id` bigint(20) DEFAULT NULL,
  `assessor_id` bigint(20) NOT NULL,
  `previous_authority_id` bigint(20) NOT NULL,
  `previous_level_id` bigint(20) NOT NULL,
  `recommended_authority_id` bigint(20) DEFAULT NULL,
  `recommended_level_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `professional_scope_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `competency_assessmen_approved_authority_i_8f201a28_fk_catalog_r` (`approved_authority_id`),
  KEY `competency_assessmen_approved_by_id_43dd39b8_fk_accounts_` (`approved_by_id`),
  KEY `competency_assessmen_approved_level_id_18e4123a_fk_catalog_r` (`approved_level_id`),
  KEY `competency_assessment_assessor_id_1363bd33_fk_accounts_user_id` (`assessor_id`),
  KEY `competency_assessmen_previous_authority_i_3376358f_fk_catalog_r` (`previous_authority_id`),
  KEY `competency_assessmen_previous_level_id_d6ae4f73_fk_catalog_r` (`previous_level_id`),
  KEY `competency_assessmen_recommended_authorit_1c9516eb_fk_catalog_r` (`recommended_authority_id`),
  KEY `competency_assessmen_recommended_level_id_86547b02_fk_catalog_r` (`recommended_level_id`),
  KEY `competency_assessment_tenant_id_cd0ddafb_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `competency_assessment_created_at_6260b57f` (`created_at`),
  KEY `competency_assessment_decision_b8271eea` (`decision`),
  KEY `competency_assessmen_professional_scope_i_927eea47_fk_competenc` (`professional_scope_id`),
  CONSTRAINT `competency_assessmen_approved_authority_i_8f201a28_fk_catalog_r` FOREIGN KEY (`approved_authority_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_assessmen_approved_by_id_43dd39b8_fk_accounts_` FOREIGN KEY (`approved_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `competency_assessmen_approved_level_id_18e4123a_fk_catalog_r` FOREIGN KEY (`approved_level_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_assessmen_previous_authority_i_3376358f_fk_catalog_r` FOREIGN KEY (`previous_authority_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_assessmen_previous_level_id_d6ae4f73_fk_catalog_r` FOREIGN KEY (`previous_level_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_assessmen_professional_scope_i_927eea47_fk_competenc` FOREIGN KEY (`professional_scope_id`) REFERENCES `competency_professional_scope` (`id`),
  CONSTRAINT `competency_assessmen_recommended_authorit_1c9516eb_fk_catalog_r` FOREIGN KEY (`recommended_authority_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_assessmen_recommended_level_id_86547b02_fk_catalog_r` FOREIGN KEY (`recommended_level_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_assessment_assessor_id_1363bd33_fk_accounts_user_id` FOREIGN KEY (`assessor_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `competency_assessment_tenant_id_cd0ddafb_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_competency_assessment_technical_score_range` CHECK (`technical_knowledge_score` >= 0 and `technical_knowledge_score` <= 100),
  CONSTRAINT `chk_competency_assessment_field_execution_score_range` CHECK (`field_execution_score` >= 0 and `field_execution_score` <= 100),
  CONSTRAINT `chk_competency_assessment_documentation_score_range` CHECK (`documentation_evidence_score` >= 0 and `documentation_evidence_score` <= 100),
  CONSTRAINT `chk_competency_assessment_ethics_score_range` CHECK (`ethics_independence_score` >= 0 and `ethics_independence_score` <= 100),
  CONSTRAINT `chk_competency_assessment_communication_score_range` CHECK (`communication_conduct_score` >= 0 and `communication_conduct_score` <= 100),
  CONSTRAINT `chk_competency_assessment_approved_level_required` CHECK (`decision` <> 'APPROVED' or `approved_level_id` is not null),
  CONSTRAINT `chk_competency_assessment_approved_authority_required` CHECK (`decision` <> 'APPROVED' or `approved_authority_id` is not null),
  CONSTRAINT `chk_competency_assessment_decision_reason_required` CHECK (`decision` <> 'REJECTED' or `decision_reason` <> ''),
  CONSTRAINT `chk_competency_assessment_approved_at_required` CHECK (`decision` not in ('APPROVED','REJECTED') or `approved_at` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `competency_assessment`
--

LOCK TABLES `competency_assessment` WRITE;
/*!40000 ALTER TABLE `competency_assessment` DISABLE KEYS */;
/*!40000 ALTER TABLE `competency_assessment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `competency_professional_scope`
--

DROP TABLE IF EXISTS `competency_professional_scope`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `competency_professional_scope` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `calendar_experience_months` int(10) unsigned NOT NULL CHECK (`calendar_experience_months` >= 0),
  `verified_field_days` decimal(8,2) NOT NULL,
  `is_deployable` varchar(30) NOT NULL,
  `verification_status` varchar(30) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `last_recalculated_at` datetime(6) DEFAULT NULL,
  `last_assessed_at` datetime(6) DEFAULT NULL,
  `complexity_rating_id` bigint(20) DEFAULT NULL,
  `current_authority_status_id` bigint(20) NOT NULL,
  `current_qualion_level_id` bigint(20) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  `scope_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `highest_authority_reached_id` bigint(20) DEFAULT NULL,
  `verified_project_count` int(10) unsigned NOT NULL CHECK (`verified_project_count` >= 0),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_professional_scope_professional_scope` (`professional_id`,`scope_id`),
  KEY `competency_professio_complexity_rating_id_a2a2bc36_fk_catalog_r` (`complexity_rating_id`),
  KEY `competency_professio_current_authority_st_624933f2_fk_catalog_r` (`current_authority_status_id`),
  KEY `competency_professio_current_qualion_leve_d0039423_fk_catalog_r` (`current_qualion_level_id`),
  KEY `competency_professional_scope_created_at_8a3475dd` (`created_at`),
  KEY `competency_professio_scope_id_ed7499ea_fk_catalog_s` (`scope_id`),
  KEY `competency_professio_tenant_id_03138546_fk_tenancy_t` (`tenant_id`),
  KEY `competency_professio_highest_authority_re_9ed05373_fk_catalog_r` (`highest_authority_reached_id`),
  CONSTRAINT `competency_professio_complexity_rating_id_a2a2bc36_fk_catalog_r` FOREIGN KEY (`complexity_rating_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_professio_current_authority_st_624933f2_fk_catalog_r` FOREIGN KEY (`current_authority_status_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_professio_current_qualion_leve_d0039423_fk_catalog_r` FOREIGN KEY (`current_qualion_level_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_professio_highest_authority_re_9ed05373_fk_catalog_r` FOREIGN KEY (`highest_authority_reached_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `competency_professio_professional_id_4475c2fa_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `competency_professio_scope_id_ed7499ea_fk_catalog_s` FOREIGN KEY (`scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `competency_professio_tenant_id_03138546_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `competency_professional_scope`
--

LOCK TABLES `competency_professional_scope` WRITE;
/*!40000 ALTER TABLE `competency_professional_scope` DISABLE KEYS */;
/*!40000 ALTER TABLE `competency_professional_scope` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=175 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-08-12 06:48:17.091313','1','superadmin@gmail.com',1,'[{\"added\": {}}]',16,1),(2,'2026-08-12 06:51:29.415700','1','Gender',1,'[{\"added\": {}}]',23,1),(3,'2026-08-12 06:51:36.061715','2','Rate Type',1,'[{\"added\": {}}]',23,1),(4,'2026-08-12 06:51:42.068266','3','Availability Status',1,'[{\"added\": {}}]',23,1),(5,'2026-08-12 06:51:47.620292','4','Role Category',1,'[{\"added\": {}}]',23,1),(6,'2026-08-12 06:51:53.789276','5','Engagement Type',1,'[{\"added\": {}}]',23,1),(7,'2026-08-12 06:52:00.827083','6','EVIDENCE_TYPE',1,'[{\"added\": {}}]',23,1),(8,'2026-08-12 06:52:07.373857','7','SOFTWARE',1,'[{\"added\": {}}]',23,1),(9,'2026-08-12 06:52:14.510377','8','EQUIPMENT',1,'[{\"added\": {}}]',23,1),(10,'2026-08-12 06:52:19.636652','9','STANDARD',1,'[{\"added\": {}}]',23,1),(11,'2026-08-12 06:52:25.127852','10','PROFESSIONAL_ROLE',1,'[{\"added\": {}}]',23,1),(12,'2026-08-12 06:52:33.305622','11','QUALIFICATION_LEVEL',1,'[{\"added\": {}}]',23,1),(13,'2026-08-12 06:52:41.944913','12','AUTHORITY_STATUS',1,'[{\"added\": {}}]',23,1),(14,'2026-08-12 06:52:47.793140','13','QUALION_LEVEL',1,'[{\"added\": {}}]',23,1),(15,'2026-08-12 06:52:53.396629','14','INDUSTRY',1,'[{\"added\": {}}]',23,1),(16,'2026-08-12 06:53:39.020561','1','INDUSTRY:1001',1,'[{\"added\": {}}]',26,1),(17,'2026-08-12 06:54:18.881227','1','INDUSTRY:IN',2,'[{\"changed\": {\"fields\": [\"Code\"]}}]',26,1),(18,'2026-08-12 06:54:35.680340','2','INDUSTRY:MF',1,'[{\"added\": {}}]',26,1),(19,'2026-08-12 06:54:51.904416','3','INDUSTRY:MO',1,'[{\"added\": {}}]',26,1),(20,'2026-08-12 06:55:06.078726','4','INDUSTRY:OG',1,'[{\"added\": {}}]',26,1),(21,'2026-08-12 06:55:36.554192','5','QUALION_LEVEL:1000',1,'[{\"added\": {}}]',26,1),(22,'2026-08-12 06:55:57.319012','6','QUALION_LEVEL:1001',1,'[{\"added\": {}}]',26,1),(23,'2026-08-12 06:56:17.437406','7','QUALION_LEVEL:1003',1,'[{\"added\": {}}]',26,1),(24,'2026-08-12 06:56:36.976832','8','QUALION_LEVEL:1004',1,'[{\"added\": {}}]',26,1),(25,'2026-08-12 06:57:13.142932','9','QUALION_LEVEL:1005',1,'[{\"added\": {}}]',26,1),(26,'2026-08-12 06:57:34.034781','10','QUALION_LEVEL:1006',1,'[{\"added\": {}}]',26,1),(27,'2026-08-12 06:57:53.038476','11','EVIDENCE_TYPE:PHOTOGRAPH',1,'[{\"added\": {}}]',26,1),(28,'2026-08-12 06:58:10.896800','12','EVIDENCE_TYPE:RESUME',1,'[{\"added\": {}}]',26,1),(29,'2026-08-12 06:58:51.721958','13','Engagement Type:2000',1,'[{\"added\": {}}]',26,1),(30,'2026-08-12 06:59:10.015918','14','Engagement Type:2001',1,'[{\"added\": {}}]',26,1),(31,'2026-08-12 06:59:24.602659','15','Engagement Type:2002',1,'[{\"added\": {}}]',26,1),(32,'2026-08-12 06:59:54.333448','16','Role Category:3000',1,'[{\"added\": {}}]',26,1),(33,'2026-08-12 07:00:08.107152','17','Role Category:3001',1,'[{\"added\": {}}]',26,1),(34,'2026-08-12 07:00:24.307472','18','Role Category:3002',1,'[{\"added\": {}}]',26,1),(35,'2026-08-12 07:01:16.179141','19','Availability Status:4000',1,'[{\"added\": {}}]',26,1),(36,'2026-08-12 07:01:34.840200','20','Availability Status:4001',1,'[{\"added\": {}}]',26,1),(37,'2026-08-12 07:02:20.236266','21','Availability Status:4002',1,'[{\"added\": {}}]',26,1),(38,'2026-08-12 07:02:43.880939','22','Availability Status:4003',1,'[{\"added\": {}}]',26,1),(39,'2026-08-12 07:03:18.573540','23','Rate Type:5000',1,'[{\"added\": {}}]',26,1),(40,'2026-08-12 07:03:33.433210','24','Rate Type:5001',1,'[{\"added\": {}}]',26,1),(41,'2026-08-12 07:03:48.862397','25','Rate Type:5002',1,'[{\"added\": {}}]',26,1),(42,'2026-08-12 07:04:21.436332','26','Gender:6000',1,'[{\"added\": {}}]',26,1),(43,'2026-08-12 07:04:40.723268','27','Gender:6001',1,'[{\"added\": {}}]',26,1),(44,'2026-08-12 07:04:57.560166','28','Gender:6003',1,'[{\"added\": {}}]',26,1),(45,'2026-08-12 07:05:41.894155','1','OceanStar',1,'[{\"added\": {}}]',9,1),(46,'2026-08-12 07:06:06.797899','1','OceanStar — INDUSTRY:IN (IN)',1,'[{\"added\": {}}]',11,1),(47,'2026-08-12 07:06:35.138181','2','OceanStar — INDUSTRY:OG (IN)',1,'[{\"added\": {}}]',11,1),(48,'2026-08-12 07:06:56.937607','2','Admin',1,'[{\"added\": {}}]',15,1),(49,'2026-08-12 07:07:13.828278','1','Super Admin',2,'[{\"changed\": {\"fields\": [\"Code\", \"Name\"]}}]',15,1),(50,'2026-08-12 07:08:33.317744','2','admin@gmail.com',1,'[{\"added\": {}}]',16,1),(51,'2026-08-12 07:17:51.257648','1','IN-BRIDGE — Bridges & Heavy Structures',1,'[{\"added\": {}}]',27,1),(52,'2026-08-12 07:18:16.644677','2','IN-CIVIL — Civil Works',1,'[{\"added\": {}}]',27,1),(53,'2026-08-12 07:18:39.845751','3','IN-STEEL — Structural Steel',1,'[{\"added\": {}}]',27,1),(54,'2026-08-12 07:19:03.591712','4','MF-COAT — Coating & Finishing',1,'[{\"added\": {}}]',27,1),(55,'2026-08-12 07:19:24.218585','5','MF-DIM — Dimensional Inspection',1,'[{\"added\": {}}]',27,1),(56,'2026-08-12 07:19:44.429035','6','MF-FAT — Factory Acceptance Test',1,'[{\"added\": {}}]',27,1),(57,'2026-08-12 07:20:06.903463','7','MF-VENDOR — Vendor Inspection',1,'[{\"added\": {}}]',27,1),(58,'2026-08-12 07:20:31.523136','8','MF-WELD — Welding & Fabrication',1,'[{\"added\": {}}]',27,1),(59,'2026-08-12 07:20:51.515003','9','MO-HSM — Hull, Structure & Machinery',1,'[{\"added\": {}}]',27,1),(60,'2026-08-12 07:21:15.440424','10','MO-MWS — Marine Warranty Survey',1,'[{\"added\": {}}]',27,1),(61,'2026-08-12 07:21:37.675214','11','MO-VESSEL — Offshore Vessel Inspection',1,'[{\"added\": {}}]',27,1),(62,'2026-08-12 07:22:02.450905','12','MO-ROPE — Rope Access Inspection',1,'[{\"added\": {}}]',27,1),(63,'2026-08-12 07:22:24.696755','13','MO-SUBSEA — Subsea / Offshore Inspection Support',1,'[{\"added\": {}}]',27,1),(64,'2026-08-12 07:22:43.476357','14','OG-COAT — Coating & Corrosion',1,'[{\"added\": {}}]',27,1),(65,'2026-08-12 07:23:06.096946','15','OG-LPM — Line Pipe Manufacturing',1,'[{\"added\": {}}]',27,1),(66,'2026-08-12 07:23:30.336577','16','OG-PIPELINE — Pipeline Construction',1,'[{\"added\": {}}]',27,1),(67,'2026-08-12 07:23:49.317143','17','OG-PRESS — Pressure Equipment',1,'[{\"added\": {}}]',27,1),(68,'2026-08-12 07:24:09.604913','18','OG-WELD — Welding & Fabrication',1,'[{\"added\": {}}]',27,1),(69,'2026-08-12 07:24:59.736349','1','SM-BRIDGE v1',1,'[{\"added\": {}}]',24,1),(70,'2026-08-12 07:25:22.191531','2','SM-CIVIL v1',1,'[{\"added\": {}}]',24,1),(71,'2026-08-12 07:25:38.896116','3','SM-COATING v1',1,'[{\"added\": {}}]',24,1),(72,'2026-08-12 07:25:58.333623','4','SM-DIMENSIONAL v1',1,'[{\"added\": {}}]',24,1),(73,'2026-08-12 07:26:14.934181','5','SM-FAT v1',1,'[{\"added\": {}}]',24,1),(74,'2026-08-12 07:26:42.238025','6','SM-HULL v1',1,'[{\"added\": {}}]',24,1),(75,'2026-08-12 07:26:58.448081','7','SM-LINEPIPE v1',1,'[{\"added\": {}}]',24,1),(76,'2026-08-12 07:27:15.111546','8','SM-MEP v1',1,'[{\"added\": {}}]',24,1),(77,'2026-08-12 07:27:36.962397','9','SM-MWS v1',1,'[{\"added\": {}}]',24,1),(78,'2026-08-12 07:27:55.722269','10','SM-PACKING v1',1,'[{\"added\": {}}]',24,1),(79,'2026-08-12 07:28:14.910007','11','SM-PIPELINE v1',1,'[{\"added\": {}}]',24,1),(80,'2026-08-12 07:28:30.140620','12','SM-PRESSURE v1',1,'[{\"added\": {}}]',24,1),(81,'2026-08-12 07:29:30.089357','13','SM-ROPE v1',1,'[{\"added\": {}}]',24,1),(82,'2026-08-12 07:29:49.568831','14','SM-STRUCTSTEEL v1',1,'[{\"added\": {}}]',24,1),(83,'2026-08-12 07:30:09.186117','15','SM-SUBSEA v1',1,'[{\"added\": {}}]',24,1),(84,'2026-08-12 07:30:28.457363','16','SM-VENDOR v1',1,'[{\"added\": {}}]',24,1),(85,'2026-08-12 07:30:46.149340','17','SM-WELD v1',1,'[{\"added\": {}}]',24,1),(86,'2026-08-12 07:45:11.531421','5','IN-BRIDGE — Bridges & Heavy Structures - SM-BRIDGE -1-0',1,'[{\"added\": {}}]',28,1),(87,'2026-08-12 07:46:10.528678','6','IN-CIVIL — Civil Works - SM-CIVIL -1-0',1,'[{\"added\": {}}]',28,1),(88,'2026-08-12 07:46:27.122148','7','IN-STEEL — Structural Steel - SM-STRUCTSTEEL -1-0',1,'[{\"added\": {}}]',28,1),(89,'2026-08-12 07:46:40.680031','8','MF-COAT — Coating & Finishing - SM-COATING -1-0',1,'[{\"added\": {}}]',28,1),(90,'2026-08-12 07:46:54.428902','9','MF-DIM — Dimensional Inspection - SM-DIMENSIONAL -1-0',1,'[{\"added\": {}}]',28,1),(91,'2026-08-12 07:47:09.758928','10','MF-FAT — Factory Acceptance Test - SM-FAT -1-0',1,'[{\"added\": {}}]',28,1),(92,'2026-08-12 07:47:24.123857','11','MF-VENDOR — Vendor Inspection - SM-VENDOR -1-0',1,'[{\"added\": {}}]',28,1),(93,'2026-08-12 07:47:38.484423','12','MF-WELD — Welding & Fabrication - SM-WELD -1-0',1,'[{\"added\": {}}]',28,1),(94,'2026-08-12 07:47:57.352303','13','MO-HSM — Hull, Structure & Machinery - SM-HULL -1-0',1,'[{\"added\": {}}]',28,1),(95,'2026-08-12 07:48:11.214839','14','MO-MWS — Marine Warranty Survey - SM-MWS -1-0',1,'[{\"added\": {}}]',28,1),(96,'2026-08-12 07:49:18.494912','18','SM-VESSEL -1',1,'[{\"added\": {}}]',24,1),(97,'2026-08-12 07:56:29.157369','15','MO-VESSEL — Offshore Vessel Inspection - SM-VESSEL -1-0',1,'[{\"added\": {}}]',28,1),(98,'2026-08-12 07:56:41.047927','16','MO-ROPE — Rope Access Inspection - SM-ROPE -1-0',1,'[{\"added\": {}}]',28,1),(99,'2026-08-12 07:56:54.127421','17','MO-SUBSEA — Subsea / Offshore Inspection Support - SM-SUBSEA -1-0',1,'[{\"added\": {}}]',28,1),(100,'2026-08-12 08:00:35.134212','18','OG-COAT — Coating & Corrosion - SM-COATING -1-0',1,'[{\"added\": {}}]',28,1),(101,'2026-08-12 08:06:32.127073','19','OG-LPM — Line Pipe Manufacturing - SM-LINEPIPE -1-0',1,'[{\"added\": {}}]',28,1),(102,'2026-08-12 08:07:21.292354','20','OG-PIPELINE — Pipeline Construction - SM-LINEPIPE -1-0',1,'[{\"added\": {}}]',28,1),(103,'2026-08-12 08:07:36.206334','21','OG-PRESS — Pressure Equipment - SM-PRESSURE -1-0',1,'[{\"added\": {}}]',28,1),(104,'2026-08-12 08:07:47.234067','22','OG-WELD — Welding & Fabrication - SM-WELD -1-0',1,'[{\"added\": {}}]',28,1),(105,'2026-08-12 08:09:36.145729','1','SM-BRIDGE -1 — sm_bridge.bridge_heavy_structure_type',1,'[{\"added\": {}}]',25,1),(106,'2026-08-12 08:13:31.344521','2','SM-BRIDGE -1 — sm_bridge.span_component_size_range',1,'[{\"added\": {}}]',25,1),(107,'2026-08-12 08:14:25.349519','3','SM-BRIDGE -1 — sm_bridge.critical_components_inspected',1,'[{\"added\": {}}]',25,1),(108,'2026-08-13 10:58:01.127776','28','AutoCAD',3,'',21,1),(109,'2026-08-13 10:58:01.127844','27','AutoCAD',3,'',21,1),(110,'2026-08-13 10:58:01.127862','26','AutoCAD',3,'',21,1),(111,'2026-08-13 10:58:01.127875','25','Ultrasonic thickness guage',3,'',21,1),(112,'2026-08-13 10:58:01.127887','24','Ultrasonic thickness guage',3,'',21,1),(113,'2026-08-13 10:58:01.127900','23','Ultrasonic thickness guage',3,'',21,1),(114,'2026-08-13 10:58:01.127911','22','ISO 9713',3,'',21,1),(115,'2026-08-13 10:58:01.127924','21','ISO 9713',3,'',21,1),(116,'2026-08-13 10:58:01.127935','20','API 5L',3,'',21,1),(117,'2026-08-13 10:58:01.127947','19','ISO 9713',3,'',21,1),(118,'2026-08-13 10:58:01.127959','18','API 5L',3,'',21,1),(119,'2026-08-13 10:58:01.127970','17','Basic',3,'',21,1),(120,'2026-08-13 10:58:01.128010','16','Hindi',3,'',21,1),(121,'2026-08-13 10:58:01.128023','15','English',3,'',21,1),(122,'2026-08-13 10:58:01.128034','14','AutoCAD',3,'',21,1),(123,'2026-08-13 10:58:01.128044','13','Ultrasonic thickness guage',3,'',21,1),(124,'2026-08-13 10:58:01.128055','12','API 5L',3,'',21,1),(125,'2026-08-13 10:58:01.128066','11','ISO 9713',3,'',21,1),(126,'2026-08-13 10:58:01.128078','10','English',3,'',21,1),(127,'2026-08-13 10:58:01.128090','9','AutoCAD',3,'',21,1),(128,'2026-08-13 10:58:01.128102','8','Ultrasonic thickness guage',3,'',21,1),(129,'2026-08-13 10:58:01.128113','5','Basic',3,'',21,1),(130,'2026-08-13 10:58:01.128124','3','Ultrasonic thickness guage',3,'',21,1),(131,'2026-08-13 11:11:34.342240','60','Hindi',3,'',21,1),(132,'2026-08-13 11:11:34.342279','59','AutoCAD',3,'',21,1),(133,'2026-08-13 11:11:34.342293','58','SAP',3,'',21,1),(134,'2026-08-13 11:11:34.342305','57','SAP',3,'',21,1),(135,'2026-08-13 11:11:34.342316','56','AutoCAD',3,'',21,1),(136,'2026-08-13 11:11:34.342327','55','SAP',3,'',21,1),(137,'2026-08-13 11:11:34.342337','54','AutoCAD',3,'',21,1),(138,'2026-08-13 11:11:34.342348','53','Ultrasonic thickness guage',3,'',21,1),(139,'2026-08-13 11:11:34.342358','52','Ultrasonic thickness guage',3,'',21,1),(140,'2026-08-13 11:11:34.342368','51','Ultrasonic thickness guage',3,'',21,1),(141,'2026-08-13 11:11:34.342380','50','ISO 9713',3,'',21,1),(142,'2026-08-13 11:11:34.342391','49','API 5L',3,'',21,1),(143,'2026-08-13 11:11:34.342401','48','Hindi',3,'',21,1),(144,'2026-08-13 11:11:34.342411','47','English',3,'',21,1),(145,'2026-08-13 11:11:34.342421','45','SAP',3,'',21,1),(146,'2026-08-13 11:11:34.342431','41','English',3,'',21,1),(147,'2026-08-13 11:11:34.342441','36','API 5L',3,'',21,1),(148,'2026-08-13 11:11:34.342451','33','AutoCAD',3,'',21,1),(149,'2026-08-13 11:11:34.342461','32','Ultrasonic thickness guage',3,'',21,1),(150,'2026-08-13 11:11:34.342472','30','ISO 9713',3,'',21,1),(151,'2026-08-18 10:04:23.428945','16','Project 1 — Sharvani Kokkonda',3,'',31,1),(152,'2026-08-18 10:04:23.428976','15','Project 1 — Sharvani Kokkonda',3,'',31,1),(153,'2026-08-18 10:04:23.429005','14','Project 1 — Sharvani Kokkonda',3,'',31,1),(154,'2026-08-18 10:04:23.429015','13','Project 1 — Sharvani Kokkonda',3,'',31,1),(155,'2026-08-18 10:04:23.429025','12','Project 1 — Sharvani Kokkonda',3,'',31,1),(156,'2026-08-18 10:04:23.429034','11','Project 1 — Sharvani Kokkonda',3,'',31,1),(157,'2026-08-18 10:04:23.429060','10','Project 1 — Sharvani Kokkonda',3,'',31,1),(158,'2026-08-18 10:04:23.429075','9','Project 1 — Sharvani Kokkonda',3,'',31,1),(159,'2026-08-18 10:04:23.429085','8','Project 1 — Sharvani Kokkonda',3,'',31,1),(160,'2026-08-18 10:04:23.429093','7','Project 1 — Sharvani Kokkonda',3,'',31,1),(161,'2026-08-18 10:04:23.429101','6','Project 1 — Sharvani Kokkonda',3,'',31,1),(162,'2026-08-18 10:04:23.429109','5','Project 1 — Sharvani Kokkonda',3,'',31,1),(163,'2026-08-18 10:04:23.429117','4','Project 1 — Sharvani Kokkonda',3,'',31,1),(164,'2026-08-18 10:04:23.429124','3','Project 1 — Sharvani Kokkonda',3,'',31,1),(165,'2026-08-18 12:47:21.530199','2','pavanimyana2000@gmail.com v1 (SUBMITTED)',2,'[{\"changed\": {\"fields\": [\"Status\"]}}]',14,1),(166,'2026-08-20 08:55:27.551361','7','rajushanigarapu1997@gmail.com',2,'[]',16,1),(167,'2026-08-20 12:13:46.450444','1','Sharvani Kokkonda',2,'[{\"changed\": {\"fields\": [\"profile_status\", \"name_display_order\", \"initial_experience_band\"]}}]',19,1),(168,'2026-08-20 12:33:00.761454','1','Sharvani Kokkonda — PROFILE_APPROVAL (PENDING)',2,'[{\"changed\": {\"fields\": [\"decision\"]}}]',22,1),(169,'2026-08-20 12:56:10.354925','1','Sharvani Kokkonda',2,'[{\"changed\": {\"fields\": [\"profile_status\"]}}]',19,1),(170,'2026-08-20 12:56:16.734698','1','Sharvani Kokkonda — PROFILE_APPROVAL (PENDING)',2,'[{\"changed\": {\"fields\": [\"decision\"]}}]',22,1),(171,'2026-08-24 11:09:54.467722','18','ABC — Pavani Myana',3,'',31,1),(172,'2026-08-25 07:52:54.615687','2','A2Z Ships',3,'',9,1),(173,'2026-08-25 08:56:43.974735','3','TenantOperation object (3)',2,'[{\"changed\": {\"fields\": [\"tenant\"]}}]',11,1),(174,'2026-08-25 09:52:59.181816','1','A2Z Ships',3,'',10,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (12,'accounts','consentrecord'),(13,'accounts','otpverification'),(14,'accounts','registrationapplication'),(15,'accounts','roles'),(16,'accounts','usertbl'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(25,'catalog','formfield'),(24,'catalog','formmodule'),(26,'catalog','referencevalue'),(23,'catalog','referencevalueoptionset'),(27,'catalog','scopecatalog'),(28,'catalog','scopemodule'),(36,'competency','competencyassessment'),(37,'competency','professionalscope'),(5,'contenttypes','contenttype'),(35,'evidence','evidencedocument'),(34,'experience','employmentrecord'),(29,'experience','exposurelog'),(30,'experience','professionalassignment'),(31,'experience','projectrecord'),(32,'experience','projectscope'),(33,'experience','scoperesponse'),(40,'governance','auditevent'),(87,'governance','calculatedfieldoverride'),(88,'governance','calculatedfieldvaluehistory'),(90,'governance','calculationrule'),(89,'governance','calculationruleset'),(21,'professionals','capabilityrecord'),(20,'professionals','contactrecord'),(17,'professionals','credentialrecord'),(18,'professionals','credentialrecorditem'),(19,'professionals','professionalprofile'),(22,'professionals','professionalreview'),(39,'resumes','resumegeneration'),(38,'resumes','resumetemplate'),(6,'sessions','session'),(44,'tenancy','candidateconsent'),(46,'tenancy','conflictofinterestdeclaration'),(42,'tenancy','dataexportrequest'),(43,'tenancy','disclosurerequest'),(41,'tenancy','module'),(10,'tenancy','organization'),(45,'tenancy','project'),(82,'tenancy','projectcandidate'),(63,'tenancy','projectmembership'),(47,'tenancy','projectplacement'),(48,'tenancy','projectrequirement'),(83,'tenancy','projectrequirementscope'),(84,'tenancy','projectscopelink'),(9,'tenancy','tenant'),(49,'tenancy','tenantapprovalmatrix'),(54,'tenancy','tenantauthorisedrepresentative'),(59,'tenancy','tenantbilling'),(50,'tenancy','tenantbranding'),(51,'tenancy','tenantbusinessunit'),(52,'tenancy','tenantcontact'),(53,'tenancy','tenantdocument'),(85,'tenancy','tenantdomain'),(86,'tenancy','tenantindustry'),(55,'tenancy','tenantintegration'),(56,'tenancy','tenantinvitation'),(74,'tenancy','tenantiprestriction'),(57,'tenancy','tenantlegalacceptance'),(58,'tenancy','tenantlegalentity'),(60,'tenancy','tenantlegalsettings'),(61,'tenancy','tenantlocation'),(62,'tenancy','tenantmembership'),(64,'tenancy','tenantmoduleentitlement'),(65,'tenancy','tenantnda'),(66,'tenancy','tenantnotificationsettings'),(67,'tenancy','tenantnumberingconfig'),(11,'tenancy','tenantoperation'),(68,'tenancy','tenantoperationlog'),(69,'tenancy','tenantreporttemplate'),(70,'tenancy','tenantresumetemplate'),(71,'tenancy','tenantroleassignment'),(72,'tenancy','tenantscope'),(73,'tenancy','tenantsecuritysettings'),(75,'tenancy','tenantsettings'),(76,'tenancy','tenantsubscription'),(77,'tenancy','tenanttaxregistration'),(78,'tenancy','tenantterminology'),(79,'tenancy','tenantverification'),(80,'tenancy','tenantworkflow'),(81,'tenancy','tenantworkflowstep'),(7,'token_blacklist','blacklistedtoken'),(8,'token_blacklist','outstandingtoken');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'accounts','0001_initial','2026-08-12 06:06:20.440909'),(2,'catalog','0001_initial','2026-08-12 06:06:20.902453'),(3,'tenancy','0001_initial','2026-08-12 06:06:21.110472'),(4,'contenttypes','0001_initial','2026-08-12 06:06:21.121846'),(5,'contenttypes','0002_remove_content_type_name','2026-08-12 06:06:21.148817'),(6,'evidence','0001_initial','2026-08-12 06:06:21.208711'),(7,'experience','0001_initial','2026-08-12 06:06:21.334523'),(8,'professionals','0001_initial','2026-08-12 06:06:23.522918'),(9,'accounts','0002_initial','2026-08-12 06:06:24.991128'),(10,'auth','0001_initial','2026-08-12 06:06:25.425966'),(11,'admin','0001_initial','2026-08-12 06:06:25.492838'),(12,'admin','0002_logentry_remove_auto_add','2026-08-12 06:06:25.500044'),(13,'admin','0003_logentry_add_action_flag_choices','2026-08-12 06:06:25.505189'),(14,'auth','0002_alter_permission_name_max_length','2026-08-12 06:06:25.542226'),(15,'auth','0003_alter_user_email_max_length','2026-08-12 06:06:25.555323'),(16,'auth','0004_alter_user_username_opts','2026-08-12 06:06:25.562388'),(17,'auth','0005_alter_user_last_login_null','2026-08-12 06:06:25.592465'),(18,'auth','0006_require_contenttypes_0002','2026-08-12 06:06:25.593820'),(19,'auth','0007_alter_validators_add_error_messages','2026-08-12 06:06:25.600078'),(20,'auth','0008_alter_user_username_max_length','2026-08-12 06:06:25.610159'),(21,'auth','0009_alter_user_last_name_max_length','2026-08-12 06:06:25.617314'),(22,'auth','0010_alter_group_name_max_length','2026-08-12 06:06:25.652353'),(23,'auth','0011_update_proxy_permissions','2026-08-12 06:06:25.687024'),(24,'auth','0012_alter_user_first_name_max_length','2026-08-12 06:06:25.696511'),(25,'competency','0001_initial','2026-08-12 06:06:26.180157'),(26,'competency','0002_initial','2026-08-12 06:06:27.206538'),(27,'evidence','0002_initial','2026-08-12 06:06:27.614291'),(28,'experience','0002_initial','2026-08-12 06:06:31.037127'),(29,'governance','0001_initial','2026-08-12 06:06:31.136102'),(30,'resumes','0001_initial','2026-08-12 06:06:31.699955'),(31,'sessions','0001_initial','2026-08-12 06:06:31.711589'),(32,'token_blacklist','0001_initial','2026-08-12 06:06:31.942753'),(33,'token_blacklist','0002_outstandingtoken_jti_hex','2026-08-12 06:06:31.958263'),(34,'token_blacklist','0003_auto_20171017_2007','2026-08-12 06:06:32.118300'),(35,'token_blacklist','0004_auto_20171017_2013','2026-08-12 06:06:32.163056'),(36,'token_blacklist','0005_remove_outstandingtoken_jti','2026-08-12 06:06:32.180916'),(37,'token_blacklist','0006_auto_20171017_2113','2026-08-12 06:06:32.195901'),(38,'token_blacklist','0007_auto_20171017_2214','2026-08-12 06:06:32.618639'),(39,'token_blacklist','0008_migrate_to_bigautofield','2026-08-12 06:06:32.780341'),(40,'token_blacklist','0010_fix_migrate_to_bigautofield','2026-08-12 06:06:32.831800'),(41,'token_blacklist','0011_linearizes_history','2026-08-12 06:06:32.833709'),(42,'token_blacklist','0012_alter_outstandingtoken_user','2026-08-12 06:06:32.876786'),(43,'experience','0003_alter_projectscope_authority_action','2026-08-13 05:35:23.996786'),(44,'experience','0004_remove_scoperesponse_uniq_scope_response_project_scope_field_group_index','2026-08-13 05:35:24.122815'),(45,'accounts','0003_registrationapplication_decision_history','2026-08-19 08:47:02.270248'),(46,'accounts','0004_alter_consentrecord_options_and_more','2026-08-19 09:13:08.351802'),(47,'catalog','0002_alter_formfield_options_alter_formmodule_options_and_more','2026-08-19 09:13:08.584695'),(48,'competency','0003_alter_competencyassessment_options_and_more','2026-08-19 09:13:08.655262'),(49,'evidence','0003_alter_evidencedocument_options','2026-08-19 09:13:08.691767'),(50,'experience','0005_alter_employmentrecord_options_and_more','2026-08-19 09:13:08.889278'),(51,'governance','0002_alter_auditevent_options','2026-08-19 09:13:08.935475'),(52,'professionals','0002_alter_professionalprofile_profile_status','2026-08-19 09:13:09.096936'),(53,'professionals','0003_alter_capabilityrecord_options_and_more','2026-08-19 09:13:09.258286'),(54,'resumes','0002_alter_resumegeneration_options_and_more','2026-08-19 09:13:09.332314'),(55,'tenancy','0002_module_alter_organization_options_and_more','2026-08-19 09:13:17.788971'),(56,'governance','0003_calculatedfieldoverride_calculatedfieldvaluehistory_and_more','2026-08-24 09:07:57.109316'),(57,'tenancy','0003_alter_organization_options_alter_tenant_options_and_more','2026-08-24 09:08:01.866225'),(58,'competency','0004_professionalscope_highest_authority_reached_and_more','2026-08-25 07:30:58.616797'),(59,'professionals','0004_professionalprofile_industries_served_and_more','2026-08-25 07:30:58.922725'),(60,'professionals','0005_alter_professionalprofile_current_classification_and_more','2026-08-25 07:30:59.334606'),(61,'governance','0004_alter_calculationrule_label','2026-08-26 10:15:35.025238'),(62,'professionals','0006_alter_contactrecord_data_classification_and_more','2026-08-26 10:15:35.268562');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('042id6qc0ue001rarmv9qknccdzvtjc3','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwC7q:RBiXhFk-qUxRoFwWLbGOyXA3uzLfRXtDZRj-Uw7gbfc','2026-09-01 05:12:38.817935'),('04edpucrdd69i70ja4djcyjp22kem17v','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wu3UH:HzA8IOx0kzCZwVmS-N-KpNVs7vdmnTuxYTOyKrP2mkw','2026-08-26 07:34:57.487597'),('0oz5p3u960rzke1uopncab7d0g3ot12p','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wxKoF:Ce9cEabeN2VEnOux2SDBY69HvVFzJtgmdG-fWQyDB30','2026-09-04 08:41:07.911482'),('1cgy615zfxrl8wtm5mcwtewopndy8n8h','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwPdK:bt-3-8OV1mb3M84MLkwKD4nRjtj4GwEa1ERCpfjFia4','2026-09-01 19:38:02.664490'),('1oevzw5ffb4k8sjubbbcq6nfcb41jkex','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wuQiV:cUvEzg8cHnuKu88-FxXD-hv7LiSiU6-v-uzsFShbgTI','2026-08-27 08:23:11.554596'),('1qfc4hypu3vno12tubz3tnybdencjubv','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wu9JW:fOvAZVDBqatS5L06Ksf4A8XjNIaDtA86_mW36hmzInI','2026-08-26 13:48:14.280047'),('1y7qi3qpr3ize8z91l17se25ijvu93r4','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwc3W:z79rHp32yd1u8pMR_RKbIKGKF81HYSJpPYS_yGOq-QA','2026-09-02 08:53:54.701866'),('2atliu2z5taqedz1mdte21pd4ese5zpm','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wx475:AzywA8aH20tMA5hZLwTudnNRJoYZRyYmvnDGBIPmCoQ','2026-09-03 14:51:27.990134'),('2juof1k3zd15ya92ddjeakwey0t8y8nd','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wuXZq:sLaHh4sy3bPBrRHedu1PS661cBhf3Z0ClokeBdy5dCo','2026-08-27 15:42:42.610882'),('2mt0bas100wmv2k127uvsgx32qcg09p1','.eJxVjEEOwiAQRe_C2hCGQhGX7nsGMgODVA0kpV0Z765NutDtf-_9lwi4rSVsnZcwJ3ERIE6_G2F8cN1BumO9NRlbXZeZ5K7Ig3Y5tcTP6-H-HRTs5VuTUVlDBM2ArJkIkLxVI2dwNo4a2Bhy58GzGRh9TF5bMyjSNrtoQYn3B-w7N7c:1wwcFu:xHWY89wNRWaqbBlFhG7qfuOdNRp0G2VlfN5X5SWXgog','2026-09-02 09:06:42.647671'),('3fuqfoaay3aqzgkw34754j25he89bqbl','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwXXd:sS11XVhjzYD9TMzd90PM0rd7_-wXCi-moj1zDJJkjrY','2026-09-02 04:04:41.242007'),('4ioier9j26ilafepifxo4hls2fjnvgyg','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwXXn:kDD7VttlCI449aJ3NuRIF49YU2WpIrynGsHfedJzbiM','2026-09-02 04:04:51.882308'),('4tlvvahjfp5t40rkblviksrn7s4vzqbi','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwJBb:a281VO5tm5mLc-TTJqx7Rty-PlaKURXNZUakZUb14qw','2026-09-01 12:44:59.881197'),('4woguoo2qc89nwwl14z6ibds3sk9rlam','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wv6u3:Lyzviv2yq6hfzmooWGx3osk62BKjr7nyrQxItnZBzoA','2026-08-29 05:25:55.440749'),('6bohny1wy9b8kuzq3idq0s3hgaricglg','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wvpXZ:9ZURwMlszzFQlbeBRPzpRSRwmjsIjarUd6xHZI_ZO9g','2026-08-31 05:05:41.016893'),('6vpkh2lhh2ldktb8a1kyu2ozs7ff9n4c','.eJxVjM0OgjAQhN9lz6Tp9gesR-8-A9m2i1RNSWg5Gd9dIMTocb75Zl6wFJ77FOGsG6icKdc9AUIDqfS01JFzTYEqr7jOCzew0_673N0f5ik8OG9FvFO-TSJMuc7Ji00RR1vEdYr8vBzu38FIZVzX3shBYUDFSKzYeyTvrGx5wM6GViEb47uTdmw0kwvRKWu09MoOXbAo4f0BhXNJXA:1wwGfW:q1sPg3q22RSauRMqWGywGS4vw1ZgDtgEcJ3NGkIJuns','2026-09-01 10:03:42.092364'),('75hsi0xyizs95ptza536c2cpujbq05ac','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wxeIY:JFmRjHUTTQpJep4RAacnJqgW2x3AADVm4Z9VZI0tgTA','2026-09-05 05:29:42.063011'),('7d5ubymovcr6u3hzgfys5k5ytr2acmsx','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wx0QM:nf5uy-OiAV6izgUOmPZELSCQ-UKzju7KdrkkCA218r8','2026-09-03 10:55:06.336091'),('8xmprv0mzvn1kmbuzr9irlh95zu6y4ud','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wuXOE:xCrCHmUVsOmoqyDajKHlqc3-zo4g3XIoiXtWIBIog3E','2026-08-27 15:30:42.662827'),('ab3w3jq5rebc7nkl9uc82wrm9vuobhzr','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wuXWs:jpzMlsXbH7seYG1oZExFvQJm31o-QfdNHYbw3FVlu0w','2026-08-27 15:39:38.047019'),('akm1he2lcz7c2relxrir0gwajzezr99q','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wujL4:Er10LxamoBC7rRgH1Kv53VR6HeFMKFqdcJeOD0DNVF8','2026-08-28 04:16:14.952200'),('bhrl62r61oqok7qavx10q3pz3pw36aav','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwdt2:Y0Gm8OMR0UfMLDdb-08G3sH46gphBsd4ccoOYqt8X8c','2026-09-02 10:51:12.499672'),('bjsghpgsdj0wdehuwixjo6rylmv9z3ww','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wu3R0:H7gUMHlkOkICUa4OqO10jP4ENDO2hctQRZBHi-iByq8','2026-08-26 07:31:34.177429'),('cfev7ojtqdrotttsgtgx4c09iuxnb3vg','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwZuQ:_6jlMe1hYW1_h-2TAdKW9EHSQCurdfEuUDjkM__aQFo','2026-09-02 06:36:22.102738'),('cpwxbs07g4hqrpppex03ja05putv2srt','eyJ1c2VyX2lkIjo2LCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wyNBM:7eFNaCcXrFtQL6TkV5tZ9bzS-9jtbQTVoYMKn8sr0Fw','2026-09-07 05:25:16.857870'),('duthz9pmm6uxrpo7p73u7z61491paah2','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwbyF:Y97qs20-d6zdvdBJ06ZGthA2f-drL9SrTl6FgVA2QqM','2026-09-02 08:48:27.661114'),('ec2glfu9wt5r7l06cx66zx1z0q2vkr08','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wxeIK:jsLEmG1V_Urt6nFNNCg8WJ_cI49VDBgG59fLcrLTkcI','2026-09-05 05:29:28.529225'),('fbeo95fgrz7c1k2aep68vq6v90rxmriq','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwIW4:U0IZrBE0vLIEdTUZXMX732rg4PeIoVjHwR8UTTWi364','2026-09-01 12:02:04.774439'),('fv8opxbyviccv8hmnzzdgqqr08phiftl','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wu3Hf:kA0o098iT5tarWCfeuGlfl0OToAEecadbWstoGkZZAw','2026-08-26 07:21:55.861251'),('fwxseupo85dwcyctr56phczfzzzqxfrt','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wuN0t:mk951Ckzam-H3D2u8THi5dcvzccviImPTnRdC9mxduM','2026-08-27 04:25:55.069463'),('gdpnml3lf361r0vc8agnss5b97sf6bx2','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wu8dI:_E9vm4E3szyZKI4zjL0J4xBktC96nZCD5UuD9LSe4cg','2026-08-26 13:04:36.296292'),('gz0ct20btssusjr1wdwxaocw8anwox7h','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wu7S1:hl1W8CLNykqnX5R2102L-x6MBzm4xhuMZel0R_SpIuc','2026-08-26 11:48:53.442696'),('hg37sobkm80r3hh6va79dz34y8sjd6bm','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wxGPx:az_K3Aec1XbkuZRMvLxpotHYj3d0wSSPaxxSjF28G-w','2026-09-04 03:59:45.045816'),('hxwm8zh11rj151aopequcywe9hvztu7y','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wxGQW:9zbSp-utHdBJcxmk-CjxS_-drDzEcyXIjFMI-02Ucfs','2026-09-04 04:00:20.603615'),('jfc7xyx9558ozs4xwize3o72jv90x25z','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wvpQB:vu57EZGya1JAqgdo3EA_MIbu7Vm0Rz6-dW2tTCK7F8A','2026-08-31 04:58:03.653068'),('jm8ygo40i0ew4o51soiryppgq78hib2b','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wurE9:3DHI1atR6Uhb2XSCQgVz3n2YwCkekNaH1dH6nyXqmu0','2026-08-28 12:41:37.587551'),('k36mysxqgukwleur1ctxnj8abuzwrvek','.eJxVjMEOgjAQRP9lz6TplhasR-9-A9ltF6makkA5Gf9dIMTocd68mRcss0xdinA2FRTJlMueAKGCNHe0lEFySYGKrLhMi1Sw0-673N0fxhQekrci3infRhXGXKbEalPU0c7qOkZ5Xg7372CgeVjXbHVvMKARJDHCjMTe6UZ6bF1oDIq13J5qL7YW8iF642yt2bi-DQ41vD-En0lb:1wxJA4:E_ZLWkdUz2KbVrf4vJA4L0ffvST_ou2w9PDiBrxoAjk','2026-09-04 06:55:32.890920'),('krts62htlzrfqklaoyjnzdc3ze96uy3x','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wuOfd:OoK7FfjzjYOl9Gviy_GXNf6iHKqtmltFWU7moagHxAY','2026-08-27 06:12:05.489378'),('kyq6svmin7gek17yjpgk7ppq49oopte2','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wwIf1:FfLup3GD-fNLiRLk3sOIrrR34uJK7SCKVywhoV3zqR8','2026-09-01 12:11:19.315921'),('lazpd8kkycgh6oaqivgee55e0uukya3c','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwIpY:BKEYZb0vn7NCtfCyxY8XkwZsM50E5GR1aSytpq95_yM','2026-09-01 12:22:12.291108'),('lkbblawl7hwxqkoolntnfa768vxvgyfd','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wu6uc:hHrmMPVHubGufDbSpr8MGqD9BsjeOo3hiEDg7EiqMOs','2026-08-26 11:14:22.979724'),('lx72nm8w4utwnv34oi2k6uqgyse3honv','eyJ1c2VyX2lkIjo2LCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wxfM3:CF8v-8o3AEnz4rIRHksxvOShz8aTC9nniX5NXEsaecI','2026-09-05 06:37:23.727239'),('mer9lzj7tu9f1n680vx9h57fsbmoh244','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wu6vM:2I8qa1lfnfyeGcTllfUSpYCHPjduSiBh5u26hU25gEY','2026-08-26 11:15:08.296364'),('mnoesk31umordk9zrk0w2twesvfjtnhd','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwurD:U3SvyPT_ZjEFWT7dQmlVP9odm6NoVLkpzHJ4WZMYmyY','2026-09-03 04:58:27.496877'),('n4o5u6w94a5rtm0t36tvlmnzq5t933pl','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwJLB:IfKFI_aefKjanwRwBj_NNwbTc1ULBiyjdTOmfJb-B8Y','2026-09-01 12:54:53.138920'),('nf55a3ajerim3jehyvzkrfcr2687eu2x','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wwXXP:sJEnuhKQ0QLraJSvXk28_ZBOValbUVn-g8IThJ0CJVM','2026-09-02 04:04:27.565432'),('oeegbkfkrxom9yw74rypc8c0kuk962cg','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwPYY:4fTKu2e3A9rPklepxg5LAqVfS7MOQwgybb-_USJGNO8','2026-09-01 19:33:06.324930'),('p68uwdmtdvo6zgwsqcwl55t870go52dn','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwIlZ:H1-2zgtd45Ac-cpQyTXKEmzfD5xmBOFOhnlXT6f2PM4','2026-09-01 12:18:05.895100'),('p7s1dul67yzp176zf6s2lh1sif5ssxmb','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwzjU:G0O_QYkMOrqWBsohQhkKqUZWRv0bQpqxjO82GuoSce8','2026-09-03 10:10:48.983251'),('pj5nv0b341262l0m46tqw2mkpr6fnzrx','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wyNBD:MRLxgOitZUsJd27m0c9cqqkRyJfqK0FDZmf9Iz9OUUU','2026-09-07 05:25:07.496680'),('ponq5xn39303wgc45dwdmkuranyv45bi','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwCQ4:sqfPBc7W_Z0x0uysbLVnuMvX5dxTg-iTvAreoKMI2oA','2026-09-01 05:31:28.987107'),('pt78c2zpl085wfy1rtjpo9ujcvcv25qa','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wwuqu:rTNEUbh91KZrkznVQ8-cnLSzIoGj2rYgZw7w_GyJwZY','2026-09-03 04:58:08.573198'),('q85jlcmd00c665n92edm8kbkxsxw6dqw','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwJEf:zis8yP0UGsgwnvJRgDRK0HOpWJt6UPvUhxfaElbbTcw','2026-09-01 12:48:09.940157'),('qchwe40oglq6ix1ct7pilytkel3phz8n','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wuOew:dGFsAswlOUolsZQWxsHc1zNZtR_Sqk8o_TbhgCO2yNM','2026-08-27 06:11:22.177200'),('qx0qzhi9ln7wi4hoaive6uj4dnblesha','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwbwn:zfkKWCSInRKOjW-1qWxU8hjJSNbkZC7exFxIPzm9zR4','2026-09-02 08:46:57.656834'),('r06f5d2km3yers47096icri0oi5v5bbq','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wvpXD:RXZxknqFGVfD0cH7_aJm6LLoUBQFFePLDfCf9183yH8','2026-08-31 05:05:19.524251'),('r0hshylkrm1rfx44vvax6x7hl8ccu9vz','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wu8jN:QNjWGaZ1SbLmvNu1P1zRN0mVdxiWFMp1qNByO7JPcKg','2026-08-26 13:10:53.572452'),('rdncbevvjlxi9ddp1grc987uqkr4l92i','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wyNB6:ThB2JrYVSir99Y1lTFG4y6je1LrzaHbP2u3mAHLQWJM','2026-09-07 05:25:00.473486'),('rg60ruk825xlmlxidpz36q9409pm7uf5','.eJxVjEEOwiAQRe_C2hCGQhGX7nsGMgODVA0kpV0Z765NutDtf-_9lwi4rSVsnZcwJ3ERIE6_G2F8cN1BumO9NRlbXZeZ5K7Ig3Y5tcTP6-H-HRTs5VuTUVlDBM2ArJkIkLxVI2dwNo4a2Bhy58GzGRh9TF5bMyjSNrtoQYn3B-w7N7c:1wwIEE:6D_UkbW5cEwAYArR9ePycs-z3rcNnPurF30a7Lz451s','2026-09-01 11:43:38.392554'),('rzn02wmcsxxua6l8acs9ifo211c39sbo','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wyqIq:aMbBcEypRuvu0hAn0slRkvZFARgvJpJQmvT2TskCV0A','2026-09-08 12:30:56.874603'),('s2184q880hdg89unzm0wpcx1s5e0e1lv','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwur3:tiP4a54oCEQEeOKv5mMHS8cItZHh6DqAzmEgqTNz3L4','2026-09-03 04:58:17.167177'),('sd7v62gxsc0ba5vyqhssfnn5yrix8xpc','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wwCPt:RsDvlDJEDtwePU-Yfdr_8rFwKhDKgeQ-UhmfghwHttA','2026-09-01 05:31:17.969364'),('si7235x3jmy0tviowbm75p9za5nf7jxj','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wxeIh:BL2_z7UP-NzzGHbY4QLS_qPu1Ay1xF7pHWzYZM-QLn4','2026-09-05 05:29:51.479270'),('tn8fjwifblqupi4cep2431oowb1e0khb','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wx1KA:JX-ZtzAxS-nPgNfcsje7G6Qwm_AjwJj58Xx7FRxkkWM','2026-09-03 11:52:46.795038'),('to8af8bxn5bylahijs93sxbr1fg0e8lv','eyJ1c2VyX2lkIjo2LCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wxJFP:t7Doi0botmcaTiEy9w7KrEkG86s9P8Y7OC8lSbE-mJ0','2026-09-04 07:01:03.649316'),('uajtcpotdtqsgl0kdbtzesycpt8joge0','eyJ1c2VyX2lkIjo2LCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wulQH:eIcmkgiImFWnh1RPFxw5ukC436llIf_qPmzBDag3QCg','2026-08-28 06:29:45.132757'),('uf6ux04frb1ra04e0aeyh9b2b51ezy3f','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wxGPZ:ax89dk4cFVFSGemDgToOJxMIYomDFQuHc6-WVtfGswU','2026-09-04 03:59:21.322456'),('ufbvfjl7x5ratyw5nv5sk6boxqetirg1','.eJxVjM0OgjAQhN9lz6Tp9gesR-8-A9m2i1RNSWg5Gd9dIMTocb75Zl6wFJ77FOGsG6icKdc9AUIDqfS01JFzTYEqr7jOCzew0_673N0f5ik8OG9FvFO-TSJMuc7Ji00RR1vEdYr8vBzu38FIZVzX3shBYUDFSKzYeyTvrGx5wM6GViEb47uTdmw0kwvRKWu09MoOXbAo4f0BhXNJXA:1wyiRb:3lMlb9h24ovnyVPEbNuhU9NxmP5Tg-BCzJ3W4nE9g7o','2026-09-08 04:07:27.303553'),('uhg223a5q4nejrkykegkw6u4ubitjs93','eyJ1c2VyX2lkIjo2LCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wymcM:vrYkW6yCIWzcytw9zSSz-3bnZAT_evfVPyJAi5wzajQ','2026-09-08 08:34:50.002401'),('v6supk11vj41927dxlo3zsqvy5v6hgp8','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wvpYA:Cj9Fxwk3RJ6T1ff7R59FmGo37H__u4PNMjTv59RQ3YE','2026-08-31 05:06:18.716972'),('v7k50thrzd7d7cz9v70ftov96bpfsdjb','eyJ1c2VyX2lkIjoyLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwbzj:wr4BR1Yxd5s9nco0qyeioY9m5sZsq5dwkRwXdI00En8','2026-09-02 08:49:59.471553'),('v8js87ocsq1hii4ifaqevu2wnv8tymq3','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wwJ5b:tJs_4wXvombeWlq_CQYOIbCb5T7FfUA1AqJMiAwElog','2026-09-01 12:38:47.492403'),('vytjmi3c1wdrw90sixi50t3qaxmgv52b','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwDOM:xGk7kj3gnqB-eUBSf1pnSRw964zfkKmwNY87TvDHfig','2026-09-01 06:33:46.001476'),('vznw7p5op5q6av8wq7xe6zofbugfwg94','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wul60:ROxU1GPVVvz-hwEsKqcGjF_o39quPOSdZrbpi1HzYzE','2026-08-28 06:08:48.045164'),('xylrb16ryl8ro9vn0d2mez93ldfw6y7l','eyJ1c2VyX2lkIjoxLCJ0ZW5hbnRfaWQiOm51bGwsImlzX2F1dGhlbnRpY2F0ZWQiOnRydWV9:1wwZsH:hOhKBiwNkSw6olv9y6zt3cmLrj4UJ7SBBkTw6qEV9Mc','2026-09-02 06:34:09.604466'),('y4whaimmt7cg6219eijk7nkrakdigc9x','eyJ1c2VyX2lkIjozLCJ0ZW5hbnRfaWQiOiIxIiwiaXNfYXV0aGVudGljYXRlZCI6dHJ1ZX0:1wwCQD:JP4YyweBnMYxvbzWDqbjnPQnEpzQtmw_kG1kAEDwxmw','2026-09-01 05:31:37.385133');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidence_document`
--

DROP TABLE IF EXISTS `evidence_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `evidence_document` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `archived_at` datetime(6) DEFAULT NULL,
  `object_id` bigint(20) unsigned NOT NULL CHECK (`object_id` >= 0),
  `file` varchar(1000) DEFAULT NULL,
  `original_file_name` varchar(255) NOT NULL,
  `mime_type` varchar(100) NOT NULL,
  `file_size` bigint(20) unsigned DEFAULT NULL CHECK (`file_size` >= 0),
  `issuer` varchar(200) NOT NULL,
  `issue_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `data_classification` varchar(30) NOT NULL,
  `resume_visibility` varchar(30) NOT NULL,
  `verification_status` varchar(30) NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `processing_status` varchar(30) NOT NULL,
  `parser_version` varchar(40) NOT NULL,
  `extracted_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`extracted_data`)),
  `user_confirmed_at` datetime(6) DEFAULT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `evidence_type_id` bigint(20) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `verified_by_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `evidence_document_content_type_id_15d14ea1_fk_django_co` (`content_type_id`),
  KEY `evidence_document_evidence_type_id_383ba64e_fk_catalog_r` (`evidence_type_id`),
  KEY `evidence_document_archived_at_071999b9` (`archived_at`),
  KEY `evidence_document_verification_status_41903ec1` (`verification_status`),
  KEY `evidence_document_processing_status_09421b06` (`processing_status`),
  KEY `evidence_document_uploaded_at_d6a7697c` (`uploaded_at`),
  KEY `evidence_document_professional_id_53716b1e_fk_professio` (`professional_id`),
  KEY `evidence_document_tenant_id_5dc35564_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `evidence_document_verified_by_id_d8718f78_fk_accounts_user_id` (`verified_by_id`),
  CONSTRAINT `evidence_document_content_type_id_15d14ea1_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `evidence_document_evidence_type_id_383ba64e_fk_catalog_r` FOREIGN KEY (`evidence_type_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `evidence_document_professional_id_53716b1e_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `evidence_document_tenant_id_5dc35564_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `evidence_document_verified_by_id_d8718f78_fk_accounts_user_id` FOREIGN KEY (`verified_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `chk_evidence_document_issue_before_expiry` CHECK (`issue_date` is null or `expiry_date` is null or `issue_date` <= `expiry_date`),
  CONSTRAINT `chk_evidence_document_verified_at_required` CHECK (`verification_status` not in ('VERIFIED','VALIDATED') or `verified_at` is not null)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidence_document`
--

LOCK TABLES `evidence_document` WRITE;
/*!40000 ALTER TABLE `evidence_document` DISABLE KEYS */;
INSERT INTO `evidence_document` VALUES (1,'b5a1e4b438e14d4d941f141fa7fc0a06',NULL,1,'oceanstar/sha656/evidence_typeresume/Survey_Approaches.pdf','Survey_Approaches.pdf','application/pdf',1924645,'',NULL,NULL,'PROFESSIONAL','CLIENT_SPECIFIC','EVIDENCE_UPLOADED',NULL,'UPLOADED','','{}',NULL,'2026-08-12 07:31:29.064023',19,12,1,1,NULL),(2,'0ca65b7eee7941b0875ea3b2e53bc7cb',NULL,1,'oceanstar/sha656/evidence_typephotograph/team.png','team.png','image/png',37398,'',NULL,NULL,'PROFESSIONAL','CLIENT_SPECIFIC','EVIDENCE_UPLOADED',NULL,'UPLOADED','','{}',NULL,'2026-08-12 07:31:29.072375',19,11,1,1,NULL),(3,'d818741f3c6d459ea7af8815a6fe2abc',NULL,2,'oceanstar/pav365/evidence_type-resume/RCard_181632528120000023.pdf','RCard_\'181632528120000023\'.pdf','application/pdf',294011,'',NULL,NULL,'PROFESSIONAL','CLIENT_SPECIFIC','EVIDENCE_UPLOADED',NULL,'UPLOADED','','{}',NULL,'2026-08-14 06:29:11.982797',19,12,2,1,NULL),(4,'3e3e21414b244f5d92076e04aaa0b847',NULL,2,'oceanstar/pav365/evidence_type-photograph/Location.jpg','Location.jpg','image/jpeg',126143,'',NULL,NULL,'PROFESSIONAL','CLIENT_SPECIFIC','EVIDENCE_UPLOADED',NULL,'UPLOADED','','{}',NULL,'2026-08-14 06:29:11.992221',19,11,2,1,NULL),(5,'adfde1dd1b8d458a80720a691c8a3b87',NULL,3,'oceanstar/raj459/evidence_type-resume/user.pdf','user.pdf','application/pdf',153422,'',NULL,NULL,'PROFESSIONAL','CLIENT_SPECIFIC','EVIDENCE_UPLOADED',NULL,'UPLOADED','','{}',NULL,'2026-08-19 12:42:38.130571',19,12,3,1,NULL),(6,'780f6573295a4b5fbc8b9309f844914f',NULL,3,'oceanstar/raj459/evidence_type-photograph/images_1.png','images (1).png','image/png',2283,'',NULL,NULL,'PROFESSIONAL','CLIENT_SPECIFIC','EVIDENCE_UPLOADED',NULL,'UPLOADED','','{}',NULL,'2026-08-19 12:42:38.142654',19,11,3,1,NULL);
/*!40000 ALTER TABLE `evidence_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experience_employment_record`
--

DROP TABLE IF EXISTS `experience_employment_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experience_employment_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `employer_organization` varchar(200) DEFAULT NULL,
  `employer_name_snapshot` varchar(200) NOT NULL,
  `job_title` varchar(160) NOT NULL,
  `country_code` varchar(2) NOT NULL,
  `city` varchar(120) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `is_current` tinyint(1) NOT NULL,
  `duties` longtext NOT NULL,
  `verification_status` varchar(30) NOT NULL,
  `resume_visibility` varchar(30) NOT NULL,
  `status` varchar(20) NOT NULL,
  `employment_type_id` bigint(20) DEFAULT NULL,
  `evidence_id` bigint(20) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `experience_employmen_employment_type_id_c4a01db3_fk_catalog_r` (`employment_type_id`),
  KEY `experience_employmen_evidence_id_7b2b9d8d_fk_evidence_` (`evidence_id`),
  KEY `experience_employment_record_created_at_54044983` (`created_at`),
  KEY `experience_employment_record_status_c074a336` (`status`),
  KEY `experience_employmen_professional_id_6c7a97da_fk_professio` (`professional_id`),
  KEY `experience_employmen_tenant_id_13ca6b78_fk_tenancy_t` (`tenant_id`),
  CONSTRAINT `experience_employmen_employment_type_id_c4a01db3_fk_catalog_r` FOREIGN KEY (`employment_type_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `experience_employmen_evidence_id_7b2b9d8d_fk_evidence_` FOREIGN KEY (`evidence_id`) REFERENCES `evidence_document` (`id`),
  CONSTRAINT `experience_employmen_professional_id_6c7a97da_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `experience_employmen_tenant_id_13ca6b78_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_employment_record_start_before_end` CHECK (`end_date` is null or `start_date` <= `end_date`),
  CONSTRAINT `chk_employment_record_is_current_end_date_consistency` CHECK (`is_current` = 0x01 and `end_date` is null or `is_current` = 0x00 and `end_date` is not null)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experience_employment_record`
--

LOCK TABLES `experience_employment_record` WRITE;
/*!40000 ALTER TABLE `experience_employment_record` DISABLE KEYS */;
INSERT INTO `experience_employment_record` VALUES (5,'2026-08-14 14:55:14.138335','2026-08-18 10:02:55.245208',NULL,'uhu','wwd','DE','Sde','2026-08-14',NULL,1,'','SELF_DECLARED','NEVER','DRAFT',NULL,NULL,1,1),(6,'2026-08-21 08:33:12.535767','2026-08-24 08:52:19.402220',NULL,'Pavani','Junior Surveyor','IN','Hyderabad','2024-01-21','2026-12-01',0,'','SELF_DECLARED','NEVER','DRAFT',NULL,NULL,2,1);
/*!40000 ALTER TABLE `experience_employment_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experience_exposure_log`
--

DROP TABLE IF EXISTS `experience_exposure_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experience_exposure_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `activity_date` date NOT NULL,
  `hours` decimal(5,2) DEFAULT NULL,
  `day_fraction` decimal(3,2) NOT NULL,
  `site_or_asset` varchar(200) NOT NULL,
  `activity_summary` longtext NOT NULL,
  `verification_status` varchar(30) NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `review_notes` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  `supervisor_professional_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `verified_by_id` bigint(20) DEFAULT NULL,
  `project_scope_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `experience_exposure_log_created_at_5de4e701` (`created_at`),
  KEY `experience_exposure_log_status_d8bd3ea3` (`status`),
  KEY `experience_exposure__professional_id_b34efde8_fk_professio` (`professional_id`),
  KEY `experience_exposure__supervisor_professio_9c70af2d_fk_professio` (`supervisor_professional_id`),
  KEY `experience_exposure_log_tenant_id_e8cc7b48_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `experience_exposure__verified_by_id_2c2b4377_fk_accounts_` (`verified_by_id`),
  KEY `experience_exposure__project_scope_id_080af4e1_fk_experienc` (`project_scope_id`),
  CONSTRAINT `experience_exposure__professional_id_b34efde8_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `experience_exposure__project_scope_id_080af4e1_fk_experienc` FOREIGN KEY (`project_scope_id`) REFERENCES `experience_project_scope` (`id`),
  CONSTRAINT `experience_exposure__supervisor_professio_9c70af2d_fk_professio` FOREIGN KEY (`supervisor_professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `experience_exposure__verified_by_id_2c2b4377_fk_accounts_` FOREIGN KEY (`verified_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `experience_exposure_log_tenant_id_e8cc7b48_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_exposure_log_hours_range` CHECK (`hours` is null or `hours` > 0 and `hours` <= 24),
  CONSTRAINT `chk_exposure_log_day_fraction_range` CHECK (`day_fraction` > 0 and `day_fraction` <= 1),
  CONSTRAINT `chk_exposure_log_supervisor_not_self` CHECK (`supervisor_professional_id` <> `professional_id` or `supervisor_professional_id` is null),
  CONSTRAINT `chk_exposure_log_verified_at_required` CHECK (`verification_status` not in ('VERIFIED','VALIDATED') or `verified_at` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experience_exposure_log`
--

LOCK TABLES `experience_exposure_log` WRITE;
/*!40000 ALTER TABLE `experience_exposure_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `experience_exposure_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experience_professional_assignment`
--

DROP TABLE IF EXISTS `experience_professional_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experience_professional_assignment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `assignment_type` varchar(30) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `allocation_percent` decimal(5,2) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `notes` longtext NOT NULL,
  `assigned_by_id` bigint(20) NOT NULL,
  `mentor_professional_id` bigint(20) DEFAULT NULL,
  `organization_id` bigint(20) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `scope_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `project_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `experience_professional_assignment_created_at_1017f5a3` (`created_at`),
  KEY `experience_professional_assignment_status_5d6a99e1` (`status`),
  KEY `experience_professio_assigned_by_id_5edf4707_fk_accounts_` (`assigned_by_id`),
  KEY `experience_professio_mentor_professional__2d7c5fef_fk_professio` (`mentor_professional_id`),
  KEY `experience_professio_organization_id_897ad20f_fk_tenancy_o` (`organization_id`),
  KEY `experience_professio_professional_id_51f75c71_fk_professio` (`professional_id`),
  KEY `experience_professio_scope_id_c5a05b6e_fk_catalog_s` (`scope_id`),
  KEY `experience_professio_tenant_id_4071e173_fk_tenancy_t` (`tenant_id`),
  KEY `experience_professio_project_id_8e7e4338_fk_experienc` (`project_id`),
  CONSTRAINT `experience_professio_assigned_by_id_5edf4707_fk_accounts_` FOREIGN KEY (`assigned_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `experience_professio_mentor_professional__2d7c5fef_fk_professio` FOREIGN KEY (`mentor_professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `experience_professio_organization_id_897ad20f_fk_tenancy_o` FOREIGN KEY (`organization_id`) REFERENCES `tenancy_organization` (`id`),
  CONSTRAINT `experience_professio_professional_id_51f75c71_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `experience_professio_project_id_8e7e4338_fk_experienc` FOREIGN KEY (`project_id`) REFERENCES `experience_project_record` (`id`),
  CONSTRAINT `experience_professio_scope_id_c5a05b6e_fk_catalog_s` FOREIGN KEY (`scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `experience_professio_tenant_id_4071e173_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_professional_assignment_start_before_end` CHECK (`end_date` is null or `start_date` <= `end_date`),
  CONSTRAINT `chk_professional_assignment_allocation_percent_range` CHECK (`allocation_percent` is null or `allocation_percent` > 0 and `allocation_percent` <= 100),
  CONSTRAINT `chk_professional_assignment_mentor_not_self` CHECK (`mentor_professional_id` <> `professional_id` or `mentor_professional_id` is null),
  CONSTRAINT `chk_professional_assignment_organization_required` CHECK (`assignment_type` not in ('BRANCH','DEPARTMENT','OPERATING_UNIT') or `organization_id` is not null),
  CONSTRAINT `chk_professional_assignment_project_required` CHECK (`assignment_type` not in ('PROJECT','TECHNICAL_REVIEW') or `project_id` is not null),
  CONSTRAINT `chk_professional_assignment_mentor_required` CHECK (`assignment_type` <> 'MENTOR' or `mentor_professional_id` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experience_professional_assignment`
--

LOCK TABLES `experience_professional_assignment` WRITE;
/*!40000 ALTER TABLE `experience_professional_assignment` DISABLE KEYS */;
/*!40000 ALTER TABLE `experience_professional_assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experience_project_record`
--

DROP TABLE IF EXISTS `experience_project_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experience_project_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `project_name` varchar(220) NOT NULL,
  `employer_organization` varchar(200) DEFAULT NULL,
  `client_organization` varchar(200) DEFAULT NULL,
  `client_name_snapshot` varchar(200) NOT NULL,
  `client_visibility` varchar(40) NOT NULL,
  `country_code` varchar(2) NOT NULL,
  `city` varchar(120) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `is_current` tinyint(1) NOT NULL,
  `allocation_percent` decimal(5,2) NOT NULL,
  `is_primary_assignment` tinyint(1) NOT NULL,
  `working_arrangement` varchar(50) NOT NULL,
  `engagement_explanation` longtext NOT NULL,
  `declared_field_days` int(10) unsigned DEFAULT NULL CHECK (`declared_field_days` >= 0),
  `verified_field_days` decimal(8,2) NOT NULL,
  `responsibilities` longtext NOT NULL,
  `achievements` longtext NOT NULL,
  `standards_applied` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`standards_applied`)),
  `verification_status` varchar(30) NOT NULL,
  `status` varchar(20) NOT NULL,
  `Experience_classification` varchar(30) DEFAULT NULL,
  `achievement_evidence_id` bigint(20) DEFAULT NULL,
  `employment_id` bigint(20) DEFAULT NULL,
  `industry_classification_id` bigint(20) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `role_title_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `verification_status_evidence_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `experience_project_record_created_at_e139bf83` (`created_at`),
  KEY `experience_project_record_status_c1c74b7d` (`status`),
  KEY `experience_project_r_achievement_evidence_4eb23be8_fk_evidence_` (`achievement_evidence_id`),
  KEY `experience_project_r_employment_id_da7c4dad_fk_experienc` (`employment_id`),
  KEY `experience_project_r_industry_classificat_d175fccb_fk_catalog_r` (`industry_classification_id`),
  KEY `experience_project_r_professional_id_122c0de7_fk_professio` (`professional_id`),
  KEY `experience_project_r_role_title_id_127f0e72_fk_catalog_r` (`role_title_id`),
  KEY `experience_project_r_tenant_id_8a1bef50_fk_tenancy_t` (`tenant_id`),
  KEY `experience_project_r_verification_status__d94314df_fk_evidence_` (`verification_status_evidence_id`),
  CONSTRAINT `experience_project_r_achievement_evidence_4eb23be8_fk_evidence_` FOREIGN KEY (`achievement_evidence_id`) REFERENCES `evidence_document` (`id`),
  CONSTRAINT `experience_project_r_employment_id_da7c4dad_fk_experienc` FOREIGN KEY (`employment_id`) REFERENCES `experience_employment_record` (`id`),
  CONSTRAINT `experience_project_r_industry_classificat_d175fccb_fk_catalog_r` FOREIGN KEY (`industry_classification_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `experience_project_r_professional_id_122c0de7_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `experience_project_r_role_title_id_127f0e72_fk_catalog_r` FOREIGN KEY (`role_title_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `experience_project_r_tenant_id_8a1bef50_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `experience_project_r_verification_status__d94314df_fk_evidence_` FOREIGN KEY (`verification_status_evidence_id`) REFERENCES `evidence_document` (`id`),
  CONSTRAINT `chk_project_record_start_before_end` CHECK (`end_date` is null or `start_date` <= `end_date`),
  CONSTRAINT `chk_project_record_is_current_end_date_consistency` CHECK (`is_current` = 0x01 and `end_date` is null or `is_current` = 0x00 and `end_date` is not null),
  CONSTRAINT `chk_project_record_allocation_percent_range` CHECK (`allocation_percent` > 0 and `allocation_percent` <= 100)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experience_project_record`
--

LOCK TABLES `experience_project_record` WRITE;
/*!40000 ALTER TABLE `experience_project_record` DISABLE KEYS */;
INSERT INTO `experience_project_record` VALUES (1,'d24280386f1247a8bf6a333864772b0e','2026-08-14 13:08:36.456843','2026-08-14 13:08:36.456872','Project 1','TCS','Client 1','Client 1','SHOW_MASKED_CLIENT_CATEGORY','IN','Karimnagar','2026-08-13',NULL,1,3.00,1,'','',5,0.00,'test','test','[]','SELF_DECLARED','DRAFT',NULL,NULL,NULL,4,1,NULL,1,NULL),(2,'96abe825946f4b91999fbfc9a99bf38d','2026-08-17 13:21:28.854056','2026-08-17 13:21:28.854079','Project 1','TCS','Client 1','Client 1','SHOW_MASKED_CLIENT_CATEGORY','IN','Karimnagar','2026-08-13',NULL,1,3.00,1,'','',5,0.00,'test','test','[]','SELF_DECLARED','DRAFT',NULL,NULL,NULL,4,1,NULL,1,NULL),(17,'96c911e70fbe4b1dbf75337f7cfd993e','2026-08-21 11:34:50.537937','2026-08-24 11:25:01.959879','ABC','Raju','ABC','ABC','SHOW_MASKED_CLIENT_CATEGORY','IN','Hyderabad','2026-08-01',NULL,1,100.00,1,'','',0,0.00,'','','[]','SELF_DECLARED','DRAFT',NULL,NULL,NULL,4,2,NULL,1,NULL);
/*!40000 ALTER TABLE `experience_project_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experience_project_scope`
--

DROP TABLE IF EXISTS `experience_project_scope`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experience_project_scope` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `activity_summary` varchar(600) NOT NULL,
  `verification_status` varchar(30) NOT NULL,
  `status` varchar(20) NOT NULL,
  `authority_action_id` bigint(20) DEFAULT NULL,
  `project_id` bigint(20) NOT NULL,
  `scope_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_project_scope_project_scope` (`project_id`,`scope_id`),
  KEY `experience_project_scope_created_at_07f4040d` (`created_at`),
  KEY `experience_project_scope_status_c7f18399` (`status`),
  KEY `experience_project_s_scope_id_d93d8476_fk_catalog_s` (`scope_id`),
  KEY `experience_project_scope_tenant_id_c28ed94e_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `experience_project_s_authority_action_id_206a341d_fk_catalog_r` (`authority_action_id`),
  CONSTRAINT `experience_project_s_authority_action_id_206a341d_fk_catalog_r` FOREIGN KEY (`authority_action_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `experience_project_s_project_id_3b5313e6_fk_experienc` FOREIGN KEY (`project_id`) REFERENCES `experience_project_record` (`id`),
  CONSTRAINT `experience_project_s_scope_id_d93d8476_fk_catalog_s` FOREIGN KEY (`scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `experience_project_scope_tenant_id_c28ed94e_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experience_project_scope`
--

LOCK TABLES `experience_project_scope` WRITE;
/*!40000 ALTER TABLE `experience_project_scope` DISABLE KEYS */;
INSERT INTO `experience_project_scope` VALUES (1,'2026-08-14 13:08:36.464434','2026-08-14 13:08:36.464463','','SELF_DECLARED','DRAFT',NULL,1,14,1),(2,'2026-08-14 13:08:36.474730','2026-08-14 13:08:36.474761','','SELF_DECLARED','DRAFT',NULL,1,15,1),(3,'2026-08-21 11:34:50.544162','2026-08-21 11:34:50.544185','','SELF_DECLARED','DRAFT',NULL,17,14,1);
/*!40000 ALTER TABLE `experience_project_scope` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experience_scope_response`
--

DROP TABLE IF EXISTS `experience_scope_response`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experience_scope_response` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `repeat_group_key` char(32) NOT NULL,
  `repeat_index` smallint(5) unsigned NOT NULL CHECK (`repeat_index` >= 0),
  `value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`value`)),
  `verification_status` varchar(30) NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `form_field_id` bigint(20) NOT NULL,
  `project_scope_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `verified_by_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `experience_scope_response_created_at_2143c4f0` (`created_at`),
  KEY `experience_scope_res_form_field_id_9826d0de_fk_catalog_f` (`form_field_id`),
  KEY `experience_scope_res_tenant_id_af8b9689_fk_tenancy_t` (`tenant_id`),
  KEY `experience_scope_res_verified_by_id_245cc1c8_fk_accounts_` (`verified_by_id`),
  KEY `experience_scope_response_project_scope_id_8b964a8a` (`project_scope_id`),
  CONSTRAINT `experience_scope_res_form_field_id_9826d0de_fk_catalog_f` FOREIGN KEY (`form_field_id`) REFERENCES `catalog_form_field` (`id`),
  CONSTRAINT `experience_scope_res_project_scope_id_8b964a8a_fk_experienc` FOREIGN KEY (`project_scope_id`) REFERENCES `experience_project_scope` (`id`),
  CONSTRAINT `experience_scope_res_tenant_id_af8b9689_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `experience_scope_res_verified_by_id_245cc1c8_fk_accounts_` FOREIGN KEY (`verified_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `chk_scope_response_verified_at_required` CHECK (`verification_status` not in ('VERIFIED','VALIDATED') or `verified_at` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experience_scope_response`
--

LOCK TABLES `experience_scope_response` WRITE;
/*!40000 ALTER TABLE `experience_scope_response` DISABLE KEYS */;
/*!40000 ALTER TABLE `experience_scope_response` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `governance_audit_event`
--

DROP TABLE IF EXISTS `governance_audit_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `governance_audit_event` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `actor_role_snapshot` varchar(80) NOT NULL,
  `action` varchar(80) NOT NULL,
  `object_id` bigint(20) unsigned NOT NULL CHECK (`object_id` >= 0),
  `before_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`before_data`)),
  `after_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`after_data`)),
  `reason` longtext NOT NULL,
  `correlation_id` char(32) NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `user_agent` longtext NOT NULL,
  `occurred_at` datetime(6) NOT NULL,
  `actor_id` bigint(20) DEFAULT NULL,
  `content_type_id` int(11) NOT NULL,
  `tenant_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `governance_audit_event_actor_id_98fe44db_fk_accounts_user_id` (`actor_id`),
  KEY `governance_audit_eve_content_type_id_73c546b7_fk_django_co` (`content_type_id`),
  KEY `governance_audit_event_tenant_id_4b1e4ea0_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `governance_audit_event_correlation_id_b4ad2e3b` (`correlation_id`),
  KEY `governance_audit_event_occurred_at_fa23c416` (`occurred_at`),
  CONSTRAINT `governance_audit_eve_content_type_id_73c546b7_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `governance_audit_event_actor_id_98fe44db_fk_accounts_user_id` FOREIGN KEY (`actor_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `governance_audit_event_tenant_id_4b1e4ea0_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `governance_audit_event`
--

LOCK TABLES `governance_audit_event` WRITE;
/*!40000 ALTER TABLE `governance_audit_event` DISABLE KEYS */;
/*!40000 ALTER TABLE `governance_audit_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `governance_calculated_field_override`
--

DROP TABLE IF EXISTS `governance_calculated_field_override`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `governance_calculated_field_override` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `object_id` bigint(20) unsigned NOT NULL CHECK (`object_id` >= 0),
  `field_name` varchar(80) NOT NULL,
  `calculation_field_code` varchar(40) NOT NULL,
  `request_type` varchar(30) NOT NULL,
  `system_calculated_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`system_calculated_value`)),
  `system_calculated_at` datetime(6) NOT NULL,
  `system_ruleset_version` varchar(30) NOT NULL,
  `proposed_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`proposed_value`)),
  `override_reason_code` varchar(40) NOT NULL,
  `rationale` longtext NOT NULL,
  `requested_at` datetime(6) NOT NULL,
  `review_notes` longtext NOT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `decision` varchar(20) NOT NULL,
  `final_approved_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`final_approved_value`)),
  `decision_reason` longtext NOT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `four_eyes_required` tinyint(1) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `review_due_date` date DEFAULT NULL,
  `approved_by_id` bigint(20) DEFAULT NULL,
  `content_type_id` int(11) NOT NULL,
  `evidence_id` bigint(20) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `requested_by_id` bigint(20) NOT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `supersedes_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `governance__content_0789c8_idx` (`content_type_id`,`object_id`,`field_name`),
  KEY `governance__profess_535d75_idx` (`professional_id`,`calculation_field_code`),
  KEY `governance_calculate_approved_by_id_552965cc_fk_accounts_` (`approved_by_id`),
  KEY `governance_calculate_evidence_id_7c9f82b4_fk_evidence_` (`evidence_id`),
  KEY `governance_calculate_requested_by_id_19328d2f_fk_accounts_` (`requested_by_id`),
  KEY `governance_calculate_reviewed_by_id_c9a494bd_fk_accounts_` (`reviewed_by_id`),
  KEY `governance_calculate_supersedes_id_5c04b676_fk_governanc` (`supersedes_id`),
  KEY `governance_calculate_tenant_id_b35822e6_fk_tenancy_t` (`tenant_id`),
  KEY `governance_calculated_field_override_created_at_f1beea11` (`created_at`),
  KEY `governance_calculated_field_calculation_field_code_5fa50997` (`calculation_field_code`),
  KEY `governance_calculated_field_override_decision_571b7187` (`decision`),
  CONSTRAINT `governance_calculate_approved_by_id_552965cc_fk_accounts_` FOREIGN KEY (`approved_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `governance_calculate_content_type_id_2631c92d_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `governance_calculate_evidence_id_7c9f82b4_fk_evidence_` FOREIGN KEY (`evidence_id`) REFERENCES `evidence_document` (`id`),
  CONSTRAINT `governance_calculate_professional_id_23aa0570_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `governance_calculate_requested_by_id_19328d2f_fk_accounts_` FOREIGN KEY (`requested_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `governance_calculate_reviewed_by_id_c9a494bd_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `governance_calculate_supersedes_id_5c04b676_fk_governanc` FOREIGN KEY (`supersedes_id`) REFERENCES `governance_calculated_field_override` (`id`),
  CONSTRAINT `governance_calculate_tenant_id_b35822e6_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_calc_override_requester_not_approver` CHECK (`requested_by_id` <> `approved_by_id` or `approved_by_id` is null),
  CONSTRAINT `chk_calc_override_final_value_required_on_approval` CHECK (`decision` <> 'APPROVED' or json_unquote(`final_approved_value`) is not null),
  CONSTRAINT `chk_calc_override_approver_required_on_approval` CHECK (`decision` <> 'APPROVED' or `approved_by_id` is not null),
  CONSTRAINT `chk_calc_override_decision_reason_required_on_rejection` CHECK (`decision` <> 'REJECTED' or `decision_reason` <> ''),
  CONSTRAINT `chk_calc_override_approved_at_required` CHECK (`decision` not in ('APPROVED','REJECTED') or `approved_at` is not null),
  CONSTRAINT `chk_calc_override_evidence_required_for_exception` CHECK (`request_type` <> 'EXCEPTIONAL_OVERRIDE' or `evidence_id` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `governance_calculated_field_override`
--

LOCK TABLES `governance_calculated_field_override` WRITE;
/*!40000 ALTER TABLE `governance_calculated_field_override` DISABLE KEYS */;
/*!40000 ALTER TABLE `governance_calculated_field_override` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `governance_calculated_field_value_history`
--

DROP TABLE IF EXISTS `governance_calculated_field_value_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `governance_calculated_field_value_history` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `object_id` bigint(20) unsigned NOT NULL CHECK (`object_id` >= 0),
  `field_name` varchar(80) NOT NULL,
  `calculation_field_code` varchar(40) NOT NULL,
  `previous_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`previous_value`)),
  `new_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`new_value`)),
  `change_source` varchar(30) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `recalculation_ruleset_version` varchar(30) NOT NULL,
  `changed_by_id` bigint(20) DEFAULT NULL,
  `content_type_id` int(11) NOT NULL,
  `override_id` bigint(20) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `governance__content_2c0373_idx` (`content_type_id`,`object_id`,`field_name`,`created_at`),
  KEY `governance__profess_a18687_idx` (`professional_id`,`calculation_field_code`,`created_at`),
  KEY `governance_calculate_changed_by_id_23ec72e0_fk_accounts_` (`changed_by_id`),
  KEY `governance_calculate_override_id_3e6f74af_fk_governanc` (`override_id`),
  KEY `governance_calculate_tenant_id_bf20fc5f_fk_tenancy_t` (`tenant_id`),
  KEY `governance_calculated_field_value_history_created_at_a3d03d20` (`created_at`),
  KEY `governance_calculated_field_calculation_field_code_e72a82b4` (`calculation_field_code`),
  KEY `governance_calculated_field_value_history_change_source_77e006ca` (`change_source`),
  CONSTRAINT `governance_calculate_changed_by_id_23ec72e0_fk_accounts_` FOREIGN KEY (`changed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `governance_calculate_content_type_id_0ca0be49_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `governance_calculate_override_id_3e6f74af_fk_governanc` FOREIGN KEY (`override_id`) REFERENCES `governance_calculated_field_override` (`id`),
  CONSTRAINT `governance_calculate_professional_id_b7e60be0_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `governance_calculate_tenant_id_bf20fc5f_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_calc_value_history_override_required` CHECK (`change_source` <> 'OVERRIDE_APPROVED' or `override_id` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `governance_calculated_field_value_history`
--

LOCK TABLES `governance_calculated_field_value_history` WRITE;
/*!40000 ALTER TABLE `governance_calculated_field_value_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `governance_calculated_field_value_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `governance_calculation_rule`
--

DROP TABLE IF EXISTS `governance_calculation_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `governance_calculation_rule` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `sequence` smallint(5) unsigned NOT NULL CHECK (`sequence` >= 0),
  `label` varchar(160) NOT NULL,
  `match_type` varchar(20) NOT NULL,
  `conditions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`conditions`)),
  `concluded_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`concluded_value`)),
  `requires_four_eyes_approval` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `rule_set_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_calc_rule_rule_set_sequence` (`rule_set_id`,`sequence`),
  KEY `governance_calculati_tenant_id_cdf7c6b6_fk_tenancy_t` (`tenant_id`),
  KEY `governance_calculation_rule_created_at_28c40d0a` (`created_at`),
  CONSTRAINT `governance_calculati_rule_set_id_c7f5a448_fk_governanc` FOREIGN KEY (`rule_set_id`) REFERENCES `governance_calculation_rule_set` (`id`),
  CONSTRAINT `governance_calculati_tenant_id_cdf7c6b6_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `governance_calculation_rule`
--

LOCK TABLES `governance_calculation_rule` WRITE;
/*!40000 ALTER TABLE `governance_calculation_rule` DISABLE KEYS */;
/*!40000 ALTER TABLE `governance_calculation_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `governance_calculation_rule_set`
--

DROP TABLE IF EXISTS `governance_calculation_rule_set`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `governance_calculation_rule_set` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `calculation_field_code` varchar(40) NOT NULL,
  `version` varchar(30) NOT NULL,
  `title` varchar(180) NOT NULL,
  `description` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `default_requires_human_confirmation` tinyint(1) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `published_at` datetime(6) DEFAULT NULL,
  `retired_at` datetime(6) DEFAULT NULL,
  `created_by_id` bigint(20) NOT NULL,
  `published_by_id` bigint(20) DEFAULT NULL,
  `scope_id` bigint(20) DEFAULT NULL,
  `supersedes_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_calc_rule_set_tenant_field_scope_version` (`tenant_id`,`calculation_field_code`,`scope_id`,`version`),
  KEY `governance_calculati_created_by_id_de31c64f_fk_accounts_` (`created_by_id`),
  KEY `governance_calculati_published_by_id_66e46cf9_fk_accounts_` (`published_by_id`),
  KEY `governance_calculati_scope_id_d12084b5_fk_catalog_s` (`scope_id`),
  KEY `governance_calculati_supersedes_id_c32fa6b9_fk_governanc` (`supersedes_id`),
  KEY `governance_calculation_rule_set_created_at_be36f9a1` (`created_at`),
  KEY `governance_calculation_rule_set_calculation_field_code_9b8ab793` (`calculation_field_code`),
  KEY `governance_calculation_rule_set_status_e708d36d` (`status`),
  CONSTRAINT `governance_calculati_created_by_id_de31c64f_fk_accounts_` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `governance_calculati_published_by_id_66e46cf9_fk_accounts_` FOREIGN KEY (`published_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `governance_calculati_scope_id_d12084b5_fk_catalog_s` FOREIGN KEY (`scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `governance_calculati_supersedes_id_c32fa6b9_fk_governanc` FOREIGN KEY (`supersedes_id`) REFERENCES `governance_calculation_rule_set` (`id`),
  CONSTRAINT `governance_calculati_tenant_id_3f2cef66_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_calc_rule_set_published_at_required` CHECK (`status` <> 'PUBLISHED' or `published_at` is not null),
  CONSTRAINT `chk_calc_rule_set_published_by_required` CHECK (`status` <> 'PUBLISHED' or `published_by_id` is not null),
  CONSTRAINT `chk_calc_rule_set_retired_at_required` CHECK (`status` <> 'RETIRED' or `retired_at` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `governance_calculation_rule_set`
--

LOCK TABLES `governance_calculation_rule_set` WRITE;
/*!40000 ALTER TABLE `governance_calculation_rule_set` DISABLE KEYS */;
/*!40000 ALTER TABLE `governance_calculation_rule_set` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professionals_capability_record`
--

DROP TABLE IF EXISTS `professionals_capability_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `professionals_capability_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `capability_type` varchar(25) NOT NULL,
  `custom_name` varchar(200) NOT NULL,
  `edition_or_model` varchar(100) NOT NULL,
  `proficiency` varchar(30) NOT NULL,
  `speaking_level` varchar(30) NOT NULL,
  `reading_level` varchar(30) NOT NULL,
  `writing_level` varchar(30) NOT NULL,
  `years_experience` decimal(5,2) DEFAULT NULL,
  `last_used_date` date DEFAULT NULL,
  `verification_status` varchar(30) NOT NULL,
  `resume_visibility` varchar(30) NOT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`details`)),
  `reference_value_id` bigint(20) DEFAULT NULL,
  `related_scope_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `professionals_capabi_reference_value_id_5c46dca2_fk_catalog_r` (`reference_value_id`),
  KEY `professionals_capabi_related_scope_id_6dd2a687_fk_catalog_s` (`related_scope_id`),
  KEY `professionals_capabi_tenant_id_f6bf52ed_fk_tenancy_t` (`tenant_id`),
  KEY `professionals_capabi_professional_id_83f01832_fk_professio` (`professional_id`),
  KEY `professionals_capability_record_created_at_ee098102` (`created_at`),
  CONSTRAINT `professionals_capabi_professional_id_83f01832_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `professionals_capabi_reference_value_id_5c46dca2_fk_catalog_r` FOREIGN KEY (`reference_value_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_capabi_related_scope_id_6dd2a687_fk_catalog_s` FOREIGN KEY (`related_scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `professionals_capabi_tenant_id_f6bf52ed_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_capability_record_custom_name_required` CHECK (`reference_value_id` is not null or `custom_name` <> ''),
  CONSTRAINT `chk_capability_record_language_levels_required` CHECK (`capability_type` <> 'LANGUAGE' or `speaking_level` <> '' and `reading_level` <> '' and `writing_level` <> ''),
  CONSTRAINT `chk_capability_record_years_experience_non_negative` CHECK (`years_experience` is null or `years_experience` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professionals_capability_record`
--

LOCK TABLES `professionals_capability_record` WRITE;
/*!40000 ALTER TABLE `professionals_capability_record` DISABLE KEYS */;
INSERT INTO `professionals_capability_record` VALUES (62,'2026-08-13 11:12:18.697038','2026-08-13 11:19:12.018794','STANDARD','API 5L','Edition 10','EXPERT','','','',NULL,'2026-07-26','SELF_DECLARED','OPTIONAL','{}',NULL,NULL,1,1),(66,'2026-08-13 11:14:22.383392','2026-08-13 11:19:12.022581','LANGUAGE','English','','','Fluent','Professional','Native / bilingual',NULL,NULL,'SELF_DECLARED','OPTIONAL','{}',NULL,NULL,1,1),(67,'2026-08-13 11:14:22.384314','2026-08-13 11:19:12.008186','EQUIPMENT','Ultrasonic thickness guage','Model 1','INDEPENDENT','','','',NULL,'2026-07-13','SELF_DECLARED','OPTIONAL','{}',NULL,NULL,1,1),(68,'2026-08-13 11:14:22.387421','2026-08-13 11:19:12.013943','SOFTWARE','AutoCAD','','INDEPENDENT','','','',5.00,'2026-05-13','SELF_DECLARED','OPTIONAL','{}',NULL,NULL,1,1),(69,'2026-08-21 09:56:23.994895','2026-08-21 10:37:18.907025','LANGUAGE','English','','','Fluent','Professional','Basic',NULL,NULL,'SELF_DECLARED','OPTIONAL','{}',NULL,NULL,1,2),(70,'2026-08-21 09:56:23.997126','2026-08-21 10:37:18.913841','STANDARD','ISO 912','Edition 5','AWARE','','','',NULL,'2026-07-31','SELF_DECLARED','OPTIONAL','{}',NULL,NULL,1,2),(71,'2026-08-21 09:56:23.997690','2026-08-21 10:37:18.893015','STANDARD','API 6l','Edition 10','SUPERVISED','','','',NULL,'2026-05-01','SELF_DECLARED','OPTIONAL','{}',NULL,NULL,1,2),(72,'2026-08-21 09:56:23.998403','2026-08-21 10:37:18.921619','EQUIPMENT','Ultrasonic thickness guage','Model 3.5','INDEPENDENT','','','',NULL,'2026-08-01','SELF_DECLARED','OPTIONAL','{\"calibration_authority\": \"Yes\"}',NULL,NULL,1,2),(73,'2026-08-21 09:56:23.999415','2026-08-21 10:37:18.888290','SOFTWARE','SAP','','INDEPENDENT','','','',5.00,'2026-08-12','SELF_DECLARED','OPTIONAL','{}',NULL,NULL,1,2);
/*!40000 ALTER TABLE `professionals_capability_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professionals_contact_record`
--

DROP TABLE IF EXISTS `professionals_contact_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `professionals_contact_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `contact_type` varchar(30) NOT NULL,
  `full_name` varchar(160) NOT NULL,
  `job_title` varchar(120) NOT NULL,
  `organization_other` varchar(200) DEFAULT NULL,
  `organization_name_snapshot` varchar(200) NOT NULL,
  `relationship` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `consent_given` tinyint(1) NOT NULL,
  `consent_given_at` datetime(6) DEFAULT NULL,
  `verification_status` varchar(30) NOT NULL,
  `resume_visibility` varchar(30) NOT NULL,
  `data_classification` varchar(30) NOT NULL,
  `organization_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `professionals_contac_organization_id_5d20e067_fk_tenancy_o` (`organization_id`),
  KEY `professionals_contac_tenant_id_91d38f54_fk_tenancy_t` (`tenant_id`),
  KEY `professionals_contac_professional_id_5f705a00_fk_professio` (`professional_id`),
  KEY `professionals_contact_record_created_at_7013ddd7` (`created_at`),
  CONSTRAINT `professionals_contac_organization_id_5d20e067_fk_tenancy_o` FOREIGN KEY (`organization_id`) REFERENCES `tenancy_organization` (`id`),
  CONSTRAINT `professionals_contac_professional_id_5f705a00_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `professionals_contac_tenant_id_91d38f54_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_contact_record_email_or_phone_required` CHECK (`email` <> '' or `phone` <> ''),
  CONSTRAINT `chk_contact_record_consent_given_at_required` CHECK (`consent_given` = 0x00 or `consent_given_at` is not null)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professionals_contact_record`
--

LOCK TABLES `professionals_contact_record` WRITE;
/*!40000 ALTER TABLE `professionals_contact_record` DISABLE KEYS */;
INSERT INTO `professionals_contact_record` VALUES (2,'2026-08-14 10:08:33.425222','2026-08-17 10:48:54.402057','PROFESSIONAL_REFERENCE','Sharvani Kokkonda','Surveyor',NULL,'A2Z','Former Supervisor','myanapavani570@gmail.com','+919676704365',0,NULL,'SELF_DECLARED','CLIENT_SPECIFIC','SENSITIVE_PII',NULL,1,1),(4,'2026-08-15 08:08:39.039727','2026-08-19 08:49:04.549446','EMERGENCY_CONTACT','kokkonda sharvani','','','','Parent','sharvanikokkonda@gmail.com','+918776565623',1,'2026-08-19 08:49:05.778000','SELF_DECLARED','NEVER','PUBLIC',NULL,1,1),(5,'2026-08-17 08:31:00.505757','2026-08-19 08:49:04.556423','EMERGENCY_CONTACT','Myana Pavani','','','','Friend','myanapavani570@gmail.com','+919676704365',1,'2026-08-19 08:49:05.777000','SELF_DECLARED','NEVER','PUBLIC',NULL,1,1),(6,'2026-08-21 10:02:00.126627','2026-08-21 10:37:25.601097','PROFESSIONAL_REFERENCE','Myana Pavani','Surveyor',NULL,'iiibets','Client','myanapavani570@gmail.com','+919676704365',1,'2026-08-21 10:37:25.859000','SELF_DECLARED','CLIENT_SPECIFIC','SENSITIVE_PII',NULL,1,2),(7,'2026-08-21 10:06:03.791858','2026-08-21 10:06:03.791892','EMERGENCY_CONTACT','Ramesh','','','','Parent','emergency@gmail.com','+919874563214',1,'2026-08-21 10:06:03.816000','SELF_DECLARED','NEVER','PUBLIC',NULL,1,2);
/*!40000 ALTER TABLE `professionals_contact_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professionals_credential_record`
--

DROP TABLE IF EXISTS `professionals_credential_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `professionals_credential_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `archived_at` datetime(6) DEFAULT NULL,
  `record_type` varchar(30) NOT NULL,
  `title` varchar(200) NOT NULL,
  `issuing_organization_other` varchar(200) DEFAULT NULL,
  `issuing_body_snapshot` varchar(200) NOT NULL,
  `issuing_country_code` varchar(2) NOT NULL,
  `discipline_or_field` varchar(160) NOT NULL,
  `level_or_grade` varchar(100) NOT NULL,
  `credential_number` text NOT NULL,
  `start_date` date DEFAULT NULL,
  `issue_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `client_organization` varchar(200) DEFAULT NULL,
  `restrictions_or_limitations` longtext NOT NULL,
  `publication_url` varchar(500) NOT NULL,
  `status` varchar(20) NOT NULL,
  `verification_status` varchar(30) NOT NULL,
  `resume_visibility` varchar(30) NOT NULL,
  `data_classification` varchar(30) NOT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`details`)),
  `secure_details` text DEFAULT NULL,
  `issuing_organization_id` bigint(20) DEFAULT NULL,
  `primary_evidence_id` bigint(20) DEFAULT NULL,
  `related_industry_id` bigint(20) DEFAULT NULL,
  `related_project_id` bigint(20) DEFAULT NULL,
  `related_scope_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `professionals_creden_professional_id_18df39b5_fk_professio` (`professional_id`),
  KEY `professionals_creden_issuing_organization_92556edc_fk_tenancy_o` (`issuing_organization_id`),
  KEY `professionals_creden_primary_evidence_id_f814dee5_fk_evidence_` (`primary_evidence_id`),
  KEY `professionals_creden_related_industry_id_3987a99c_fk_catalog_r` (`related_industry_id`),
  KEY `professionals_creden_related_project_id_31f3ac6d_fk_experienc` (`related_project_id`),
  KEY `professionals_creden_related_scope_id_94dad59c_fk_catalog_s` (`related_scope_id`),
  KEY `professionals_creden_tenant_id_3342d4d3_fk_tenancy_t` (`tenant_id`),
  KEY `professionals_credential_record_created_at_6b7c2ce2` (`created_at`),
  KEY `professionals_credential_record_archived_at_b699bd7e` (`archived_at`),
  KEY `professionals_credential_record_status_b0593d58` (`status`),
  CONSTRAINT `professionals_creden_issuing_organization_92556edc_fk_tenancy_o` FOREIGN KEY (`issuing_organization_id`) REFERENCES `tenancy_organization` (`id`),
  CONSTRAINT `professionals_creden_primary_evidence_id_f814dee5_fk_evidence_` FOREIGN KEY (`primary_evidence_id`) REFERENCES `evidence_document` (`id`),
  CONSTRAINT `professionals_creden_professional_id_18df39b5_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `professionals_creden_related_industry_id_3987a99c_fk_catalog_r` FOREIGN KEY (`related_industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_creden_related_project_id_31f3ac6d_fk_experienc` FOREIGN KEY (`related_project_id`) REFERENCES `experience_project_record` (`id`),
  CONSTRAINT `professionals_creden_related_scope_id_94dad59c_fk_catalog_s` FOREIGN KEY (`related_scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `professionals_creden_tenant_id_3342d4d3_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_credential_record_start_before_end` CHECK (`start_date` is null or `end_date` is null or `start_date` <= `end_date`),
  CONSTRAINT `chk_credential_record_issue_before_expiry` CHECK (`issue_date` is null or `expiry_date` is null or `issue_date` <= `expiry_date`),
  CONSTRAINT `chk_credential_record_issuing_body_required` CHECK (`issuing_organization_id` is not null or `issuing_body_snapshot` <> '')
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professionals_credential_record`
--

LOCK TABLES `professionals_credential_record` WRITE;
/*!40000 ALTER TABLE `professionals_credential_record` DISABLE KEYS */;
INSERT INTO `professionals_credential_record` VALUES (4,'2026-08-14 11:59:54.738685','2026-08-17 10:48:53.905522',NULL,'MEMBERSHIP','Institution',NULL,'Institution','','','Grade 1','gAAAAABqgucVHtyp7hLg9ZWZjO2qNaZiQS-CYjyVcOBCkwuIOOrQXS2zd4i_5L-yGGb0XbiYfKLE8HUR0YXKInfBPJDunPdUHg==','2026-09-01',NULL,NULL,NULL,NULL,'','','EXPIRED','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(5,'2026-08-14 11:59:54.741855','2026-08-17 10:48:53.913130',NULL,'PUBLICATION','Publication 123',NULL,'Publisher','','','','',NULL,'2026-09-05',NULL,NULL,NULL,'','https://www.youtube.com/','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(6,'2026-08-14 11:59:54.746401','2026-08-17 10:48:53.914966',NULL,'AWARD','Award',NULL,'Issuer 123','','','','',NULL,'2026-09-05',NULL,NULL,NULL,'Context','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(7,'2026-08-17 10:04:44.719386','2026-08-19 08:49:05.191653',NULL,'MEDICAL_FITNESS','routine',NULL,'Clinic','','','routine','',NULL,'2026-08-17','2029-01-17',NULL,NULL,'Nothing','','ARCHIVED','SELF_DECLARED','NEVER','PUBLIC','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(9,'2026-08-17 10:45:29.519696','2026-08-17 10:45:29.519726',NULL,'PASSPORT','Passport',NULL,'India','IN','','','gAAAAABqguZJBIF3T405DGe70qiPIsyYKLH_I-Y_DSN6zZ45Jl6cFAnP1W8TNoC_TMrylPtzZpl0HUJFvPdO1MOqhuzDR4m-xQ==',NULL,NULL,'2030-01-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(10,'2026-08-17 10:45:29.530539','2026-08-21 09:49:21.493473',NULL,'MARINE_CDC','CDC / Seaman Book',NULL,'United Kingdom','GB','','','gAAAAABqiB8hV1r8HKJf3BP4aR2VGtLVXrjjL9S35kgGd3Kv83HqpSXT92CSOl-e8tntqTyKSpeLVwgJ63KYCr1PEosNZ9dRFPNlWe7FLxCg_urQDOnWNhc1pzlbca89l36U4ALiXg8VSZOP8LFdgfI5IZr1ZA8DiTNhK6F8039MmO4KBh-hPdkMgo5xZXk6uQRrOjKA_7iF-XRcIWzo0GBJGnAEzEz5rQ==',NULL,'2026-08-17','2030-01-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(14,'2026-08-17 10:46:59.633738','2026-08-17 10:46:59.633768',NULL,'PASSPORT','Passport',NULL,'India','IN','','','gAAAAABqguajKPcoHHsRghXKGMGVIBJMT3yPa_9axBeW8FNzbW3tOguMET5QTxIlfi4l0T6DWT5sia5Ol-83Om8i5djxtE-1Jw==',NULL,NULL,'2030-01-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(16,'2026-08-17 10:46:59.655919','2026-08-21 09:49:21.479189',NULL,'MARINE_COC','Certificate of Competency',NULL,'Issuing Authority','','','Chief Engineer','gAAAAABqiB8hR9Fb12Dv5l8I3YFOhZy7QiJNWnrVy7iCRFAjXva7T7DBZs9apjs9_d9Jo_xX5oEJcXOge0ah_ryq38PjJza4KQLacYe5uzIm_v5AQFid7Fm7BDfLmks9e_nUwE5EwbtsvlJFqf-3rCsEbI5awfWRSy8do3gpCLEcPU5he4_br8aUoqpxvOKRyJu7Q-t_ZjN7wQ2yErUAdiyT5zS6JngVdg==',NULL,'2026-08-21','2030-04-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(19,'2026-08-17 10:47:08.402024','2026-08-17 10:47:08.402057',NULL,'PASSPORT','Passport',NULL,'India','IN','','','gAAAAABqguashzEgzYSmOjZ7bAel-FY0vMACGGHNqruVau66R01YHZGnDMEt4kzbdJyptzhidjM7R6C6A2c1NJkubMPsCyPVig==',NULL,NULL,'2030-01-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(24,'2026-08-17 10:51:14.073941','2026-08-17 10:51:14.073970',NULL,'PASSPORT','Passport',NULL,'India','IN','','','gAAAAABqgueidxsPzco9ckV6nR7wk8vQNMtahnBCliEWeLd0H0TvCUWeW2BqXHjnJx-vSv3i_5qCc2BDRE2phlWW5RaALqZYSA==',NULL,NULL,'2030-01-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(29,'2026-08-18 06:37:43.199482','2026-08-18 06:37:43.199513',NULL,'PASSPORT','Passport',NULL,'India','IN','','','gAAAAABqg_23oj1pZGlVJRsxM-IFcViTywmQf9q7nvCpDudgQvqM_51CZU1U34Uh-yJx6uOKm6rcQRAarbvnp75n_81ASNcdMKcIr_X0LO4a3qj6dgTH3Vx_PTrXfqVHl3tRdaif1slwpdIHTppb52sHC6s3ZeaZpq_d1dQxsTQtJNcjGNkhkX7o2LivlbGw-WvGCbJkJTeJ29xr7VNTScYOZJ28GXquKQ==',NULL,NULL,'2030-01-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(36,'2026-08-18 06:37:43.292392','2026-08-21 09:49:21.473083',NULL,'EDUCATION','Bachelor of Engineering',NULL,'Bachelor of Engineering','IN','Bachelor of Engineering','Grade123','','2026-10-17',NULL,NULL,'2030-09-17',NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(42,'2026-08-18 06:38:17.034884','2026-08-21 09:49:21.497817',NULL,'PASSPORT','Passport',NULL,'India','IN','','','gAAAAABqiB8h93XUDv0PxilEr3rR-1TNf23EnF28N3dZcnw3dP5iTdWmxOXyqdATH7hjTMY4ybnHSI3iJ6wGXTBv4BsTgaP6HhRCkML7qhTeXdz9RPI_EPocqFCAtCOfRp-1fHv7_1Ci4Y4YJaYsTNZj4rkMk9OdGrpsMBb7v4jFtaIlcujw23Edptk9379JCWanr-u5QcmN6EPyNgMqnl_RNxXFPiesXg==',NULL,NULL,'2030-01-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(50,'2026-08-18 06:38:17.059713','2026-08-21 09:49:21.489348',NULL,'CERTIFICATION','AWS123',NULL,'AWS','','','Level 1','gAAAAABqiB8hbZ7Oggq8bUiV8eTS1_JlNjYPrSiIj3VJilgJx1ZnLxWp70h2SrybCE2i-jwtcH5rLXNR5MK__BsKm3XFW7qeJp8bWM_bQETi9esTsF_ZVWqqnL6Oe0tULAny4vVWDjUA7gc0wjJZTH98k_TYP23ttxO_iwXY8uz7iS8VxKlA_ZXdQ_ZIanJRQCBL-Mgl9ayttF_iZq1bJgBf2XVlf9VOOA==',NULL,'2026-08-19','2030-01-17',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{\"linked_scope\": \"NDT \"}',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(51,'2026-08-21 07:09:00.813669','2026-08-21 10:37:03.174790',NULL,'PASSPORT','Passport',NULL,'India','IN','','','gAAAAABqiCpPmLWFfliXfdSQI3eQZw5brz36OyQXQCsTDICIVaB6U1R4JREuDFM9hCOygA_gjKjMnIbj8P-_9jiQYT9N0plr4g==',NULL,NULL,'2029-09-01',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(52,'2026-08-21 07:09:00.827228','2026-08-21 10:37:03.147921',NULL,'MARINE_CDC','CDC / Seaman Book',NULL,'India','IN','','','gAAAAABqiCpPmOETCoKNi3Ehv2rU1yAt0cccoZWCTtWw5cBDT3cn4AeceCWqLYntbWFHfyQ__pDaM4QGaA4n75j0u2Wv_zO2zQ==',NULL,'2026-01-21','2030-06-02',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(53,'2026-08-21 07:09:00.830930','2026-08-21 10:37:03.142143',NULL,'MARINE_COC','Certificate of Competency',NULL,'Issuing authority','','','Marine Master','gAAAAABqiCpPh1bKTAvREykPSMDFxSpRAFrKn1kUn8lUu5VArRSLq3A59Mw-ZELZYWDdlYT8jRZVIEwIyuQzBjC4p9IPMpNnnw==',NULL,'2026-01-21','2029-09-21',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(54,'2026-08-21 07:09:00.850273','2026-08-21 10:37:03.188210',NULL,'EDUCATION','Mechanical Engineering',NULL,'OU','IN','Mechanical Engineering','First Class','','2025-05-01',NULL,NULL,'2029-01-21',NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(55,'2026-08-21 07:09:00.855936','2026-08-21 10:37:03.166970',NULL,'CERTIFICATION','CSWP 3.1',NULL,'AWS','','','Level 2','gAAAAABqiCpP0emq--F8a9x2UCSSGSEWwvhG01paX6N8AsDh9aENA90KC1RvFv_lB0KdSQu6UIsJKXubS3dGBTbCc92tg2icQA==',NULL,'2026-01-21','2031-08-21',NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{\"linked_scope\": \"NDT\"}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(56,'2026-08-21 07:09:00.860079','2026-08-21 10:37:03.196963',NULL,'TRAINING','SUrveyor Course',NULL,'Manoj','','','','','2026-01-21',NULL,'2033-10-28','2029-06-21',NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(60,'2026-08-21 10:01:59.233476','2026-08-21 10:37:25.137793',NULL,'MEMBERSHIP','Osmania',NULL,'Osmania','','','Grade1','gAAAAABqiCplTnxunBrFX5o26HIE5PvOzzEr_zBXK9fud-5mr3kad-z4XVQDoA36u1LzsRBBOtJWHkjD3OhfCTPe40NcUeJiUA==','2024-06-04',NULL,NULL,NULL,NULL,'','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(61,'2026-08-21 10:01:59.236330','2026-08-21 10:37:25.153296',NULL,'PUBLICATION','ABC',NULL,'SaiKumar','','','','',NULL,'2026-08-01',NULL,NULL,NULL,'','https://www.youtube.com/','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(62,'2026-08-21 10:01:59.238527','2026-08-21 10:37:25.145866',NULL,'AWARD','ABC',NULL,'ABC','','','','',NULL,'2026-08-14',NULL,NULL,NULL,'Context','','ACTIVE','SELF_DECLARED','OPTIONAL','PROFESSIONAL','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(63,'2026-08-21 10:06:04.334929','2026-08-21 10:06:04.334954',NULL,'MEDICAL_FITNESS','routine',NULL,'Clinic','','','routine','',NULL,'2026-08-01','2030-05-01',NULL,NULL,'','','ACTIVE','SELF_DECLARED','NEVER','PUBLIC','{}',NULL,NULL,NULL,NULL,NULL,NULL,1,2),(64,'2026-08-24 10:48:09.542672','2026-08-24 11:10:30.411677',NULL,'CLIENT_APPROVAL','Manoj','Manoj','Manoj','','','','gAAAAABqjCam8UQ1ujdgQ-g7qaTbOEDqJUPhbRF_LRQYHPs39knQIaw83y2vGhfYAASZcC7R5xClPpWGKblwKhR9ftlv_UPesw==',NULL,'2026-08-01','2027-12-24',NULL,'Manoj','','','ACTIVE','SELF_DECLARED','NEVER','PUBLIC','{\"field\": \"Surveyor\"}',NULL,NULL,NULL,NULL,17,NULL,1,2);
/*!40000 ALTER TABLE `professionals_credential_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professionals_credentialrecorditem`
--

DROP TABLE IF EXISTS `professionals_credentialrecorditem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `professionals_credentialrecorditem` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `item_type` varchar(50) NOT NULL,
  `title` varchar(200) NOT NULL,
  `item_number` text NOT NULL,
  `country_code` varchar(2) NOT NULL,
  `issue_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`details`)),
  `credential_record_id` bigint(20) NOT NULL,
  `evidence_document_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `professionals_creden_credential_record_id_4ba6357f_fk_professio` (`credential_record_id`),
  KEY `professionals_creden_evidence_document_id_49571d26_fk_evidence_` (`evidence_document_id`),
  KEY `professionals_creden_tenant_id_22d5740a_fk_tenancy_t` (`tenant_id`),
  KEY `professionals_credentialrecorditem_created_at_421b7b6c` (`created_at`),
  CONSTRAINT `professionals_creden_credential_record_id_4ba6357f_fk_professio` FOREIGN KEY (`credential_record_id`) REFERENCES `professionals_credential_record` (`id`),
  CONSTRAINT `professionals_creden_evidence_document_id_49571d26_fk_evidence_` FOREIGN KEY (`evidence_document_id`) REFERENCES `evidence_document` (`id`),
  CONSTRAINT `professionals_creden_tenant_id_22d5740a_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professionals_credentialrecorditem`
--

LOCK TABLES `professionals_credentialrecorditem` WRITE;
/*!40000 ALTER TABLE `professionals_credentialrecorditem` DISABLE KEYS */;
INSERT INTO `professionals_credentialrecorditem` VALUES (1,'2026-08-17 10:45:29.523487','2026-08-17 10:45:29.523515','VISA_WORK_PERMIT','Work Visa','gAAAAABqguZJPe6-mg60s9kd6yRmRBMD67ovz_ydplV9TjgofrNRkz3OZD3y2w3eJ6kbu9nuWnh7D0JxPfzN2DTYfYoBfQ8wVQ==','IN','2026-08-29','2030-05-17','ACTIVE','{}',9,NULL,1),(2,'2026-08-17 10:46:59.637363','2026-08-17 10:46:59.637383','VISA_WORK_PERMIT','Work Visa','gAAAAABqguaj_SVtGgruW65_DMbycnOCvnwEb8XQCRQWKjV-y2OXYjBib745Kq9aihGJ3UTH8j2dmd89u-oPR1T57rMLA_Nhig==','IN','2026-08-29','2030-05-17','ACTIVE','{}',14,NULL,1),(3,'2026-08-17 10:47:08.406827','2026-08-17 10:47:08.406859','VISA_WORK_PERMIT','Work Visa','gAAAAABqguasPEVhzvXgl4ny3KMHGnSWFQw2kvtu2MtkWEak-2QsiN7wbqeq2zhXplk4zMam2mOqLxxoLuvUBPJwfnP345nj0Q==','IN','2026-08-29','2030-05-17','ACTIVE','{}',19,NULL,1),(4,'2026-08-17 10:51:14.075586','2026-08-17 10:51:14.075608','VISA_WORK_PERMIT','Work Visa','gAAAAABqgueik_HvQPDGZYtlEnNoMCIyH94pe5sK777OBhce5kTcoNlEXqnfVDejYbgpw9q19iJfzEzNw4JO-Xy9P7ov3zaChg==','IN','2026-08-29','2030-05-17','ACTIVE','{}',24,NULL,1),(5,'2026-08-17 10:51:14.078315','2026-08-17 10:51:14.078332','VISA_WORK_PERMIT','BUsiness Visa','gAAAAABqgueiWEpZyd3v0sQMkGwJ4ZhN5P5m0ONhUjEvDssVTRt0j4lzZNTjLll43ga9eUaBzAOZBieg2e1jWEuoYjJUIrOVzQ==','US','2026-08-17','2030-11-17','ACTIVE','{}',24,NULL,1),(6,'2026-08-18 06:37:43.245549','2026-08-18 06:37:43.245581','VISA_WORK_PERMIT','Work Visa','gAAAAABqg_23mPtGwevTEeakr-3_-rKNaU1n3Rlnvi2jh5lOgmZfDIJ-pkpN8trbcGClgR9BsuuN6A9YXPPs2CVTqDDb1UkB7iu-w5tzvwbYIDgkzlucgLY-LeMBRU2EGQtWio_yEWBnKFey-JV367NecCRSBK1TpSFWASQIF6u3WLMwtVSdBqvWSdEvuW0wDVO6ajUMu_DZgfVbHBCDmXNv-TL-v1zGmQ==','AE','2026-08-29','2030-05-17','ACTIVE','{}',29,NULL,1),(7,'2026-08-18 06:37:43.247353','2026-08-18 06:37:43.247374','VISA_WORK_PERMIT','BUsiness Visa','gAAAAABqg_238AXCMis-YU3-3OVna0eMB87BefJZOsAE54lYAHEUPQBko7uGrBLd-vC0wLVyrpGdicaiq_GJwF6Z1CN810QVtNBpd_Z5S_kKSRwLCkyb1b-Ogl3MCC7dxcTLSHv8pKa5_Jc-b65M5391ULcQQaWoGxXWJH7NNLaNlM0Q5JGS9ptG5QLR1Cj-KC5DP74CCHz6dT1ymwpKg2rkvYCBwwlVMQ==','US','2026-08-17','2030-11-17','ACTIVE','{}',29,NULL,1),(8,'2026-08-18 06:38:17.038587','2026-08-18 06:38:17.038613','VISA_WORK_PERMIT','Work Visa','gAAAAABqg_3ZlW2IjFdaGOwscCVDiYHL-qj3U2-zt2WR3D-aZCIytWwiTeXUVsbMgi3olqrIE3H_TxcBvEhbBbPFQn-yvwFDyZywQiWF6t7U8c11gtG8UQd5Yx3-H7joaikcxoNDsTz_JhrcRsJfTxFX_uo_d8k4KrZCOVJHn3ZPw_orBbeQWREUhJqNW3c15_rjPlHxcSNjQMigTZ_hTXV1KRvQt7McOw==','AE','2026-08-29','2030-05-17','ACTIVE','{}',42,NULL,1),(9,'2026-08-18 06:38:17.040651','2026-08-18 06:38:17.040856','VISA_WORK_PERMIT','BUsiness Visa','gAAAAABqg_3Z7mtr0bho7gACQzE4m79aD-QfwhhHUjBBX4do1eYycXeMw5Ly_bsVy-aqJdZrsfOEtG2hTOj8Jh5Zi87m1fzNFTk_bDZWwQXB_xIMkPKSTT5VJBCbs-u25vX3HXlmUY1yDR6Y56L-C_NnMi1GfitcN1kuFuG9s9GhKzcEgTtfg85_FxXAXyQLKWk6_tsUOmmtFDl4BgkyOKasgjyZpwJl6A==','US','2026-08-17','2030-11-17','ACTIVE','{}',42,NULL,1),(10,'2026-08-21 07:09:00.821153','2026-08-21 07:09:00.821188','VISA_WORK_PERMIT','Work Visa','gAAAAABqh_mMSAhVczddRn1KX7MtMY-ndG3Xibtp2STMHqwMGqvaf2S39Brct1Qi_EbcK5tWRfCC29lOYAzlPRbBZDKFuTa9Hw==','IN','2025-01-01','2030-12-01','ACTIVE','{}',51,NULL,1);
/*!40000 ALTER TABLE `professionals_credentialrecorditem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professionals_professional_profile`
--

DROP TABLE IF EXISTS `professionals_professional_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `professionals_professional_profile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `profile_status` varchar(30) NOT NULL,
  `current_classification` varchar(20) NOT NULL,
  `classification_status` varchar(30) NOT NULL,
  `classified_at` datetime(6) DEFAULT NULL,
  `classification_ruleset_version` varchar(30) NOT NULL,
  `profile_version` int(10) unsigned NOT NULL CHECK (`profile_version` >= 0),
  `completion_percent` decimal(5,2) NOT NULL,
  `legal_full_name` varchar(160) NOT NULL,
  `display_name` varchar(160) NOT NULL,
  `first_name` varchar(80) NOT NULL,
  `middle_name` varchar(80) NOT NULL,
  `last_name` varchar(80) NOT NULL,
  `preferred_name` varchar(80) NOT NULL,
  `name_display_order` varchar(20) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `nationalities` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`nationalities`)),
  `country_of_residence` varchar(2) NOT NULL,
  `city` varchar(120) NOT NULL,
  `timezone` varchar(64) NOT NULL,
  `address_line_1` text NOT NULL,
  `address_line_2` text NOT NULL,
  `postal_code` text NOT NULL,
  `address_country_code` varchar(2) NOT NULL,
  `personal_email` varchar(254) NOT NULL,
  `primary_phone` varchar(20) NOT NULL,
  `linkedin_url` varchar(500) NOT NULL,
  `photo_resume_visibility` varchar(30) NOT NULL,
  `current_job_title` varchar(120) NOT NULL,
  `initial_experience_band` varchar(20) NOT NULL,
  `headline` varchar(140) NOT NULL,
  `summary` longtext NOT NULL,
  `key_strengths` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`key_strengths`)),
  `additional_roles` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`additional_roles`)),
  `summary_source` varchar(20) NOT NULL,
  `available_from` date DEFAULT NULL,
  `notice_period_days` smallint(5) unsigned DEFAULT NULL CHECK (`notice_period_days` >= 0),
  `engagement_types` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`engagement_types`)),
  `preferred_locations` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`preferred_locations`)),
  `offshore_ready` tinyint(1) NOT NULL,
  `expected_rate` decimal(14,2) DEFAULT NULL,
  `rate_currency` varchar(3) NOT NULL,
  `ppe_sizes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`ppe_sizes`)),
  `submitted_at` datetime(6) DEFAULT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `availability_status_id` bigint(20) DEFAULT NULL,
  `classified_by_id` bigint(20) DEFAULT NULL,
  `existing_resume_id` bigint(20) DEFAULT NULL,
  `gender_id` bigint(20) DEFAULT NULL,
  `highest_qualification_level_id` bigint(20) DEFAULT NULL,
  `primary_industry_id` bigint(20) DEFAULT NULL,
  `primary_role_id` bigint(20) DEFAULT NULL,
  `primary_scope_id` bigint(20) DEFAULT NULL,
  `profile_photo_evidence_id` bigint(20) DEFAULT NULL,
  `rate_type_id` bigint(20) DEFAULT NULL,
  `registration_application_id` bigint(20) NOT NULL,
  `self_declared_career_stage_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `industries_served` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`industries_served`)),
  `total_career_experience_months` int(10) unsigned NOT NULL CHECK (`total_career_experience_months` >= 0),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `registration_application_id` (`registration_application_id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `uniq_professional_profile_tenant_user` (`tenant_id`,`user_id`),
  KEY `professionals_profes_availability_status__d5246623_fk_catalog_r` (`availability_status_id`),
  KEY `professionals_profes_classified_by_id_7ac5b42c_fk_accounts_` (`classified_by_id`),
  KEY `professionals_profes_existing_resume_id_404e7fbb_fk_evidence_` (`existing_resume_id`),
  KEY `professionals_profes_gender_id_28f16b03_fk_catalog_r` (`gender_id`),
  KEY `professionals_profes_highest_qualificatio_4b9bfa17_fk_catalog_r` (`highest_qualification_level_id`),
  KEY `professionals_profes_primary_industry_id_d029def9_fk_catalog_r` (`primary_industry_id`),
  KEY `professionals_profes_primary_role_id_2111ffdb_fk_catalog_r` (`primary_role_id`),
  KEY `professionals_profes_primary_scope_id_906d3b55_fk_catalog_s` (`primary_scope_id`),
  KEY `professionals_profes_profile_photo_eviden_c8383e94_fk_evidence_` (`profile_photo_evidence_id`),
  KEY `professionals_profes_rate_type_id_f8be2161_fk_catalog_r` (`rate_type_id`),
  KEY `professionals_profes_self_declared_career_07ff4fb8_fk_catalog_r` (`self_declared_career_stage_id`),
  KEY `professionals_professional_profile_created_at_d1814e41` (`created_at`),
  KEY `professionals_professional_profile_profile_status_d3f6f303` (`profile_status`),
  CONSTRAINT `professionals_profes_availability_status__d5246623_fk_catalog_r` FOREIGN KEY (`availability_status_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_profes_classified_by_id_7ac5b42c_fk_accounts_` FOREIGN KEY (`classified_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `professionals_profes_existing_resume_id_404e7fbb_fk_evidence_` FOREIGN KEY (`existing_resume_id`) REFERENCES `evidence_document` (`id`),
  CONSTRAINT `professionals_profes_gender_id_28f16b03_fk_catalog_r` FOREIGN KEY (`gender_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_profes_highest_qualificatio_4b9bfa17_fk_catalog_r` FOREIGN KEY (`highest_qualification_level_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_profes_primary_industry_id_d029def9_fk_catalog_r` FOREIGN KEY (`primary_industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_profes_primary_role_id_2111ffdb_fk_catalog_r` FOREIGN KEY (`primary_role_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_profes_primary_scope_id_906d3b55_fk_catalog_s` FOREIGN KEY (`primary_scope_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `professionals_profes_profile_photo_eviden_c8383e94_fk_evidence_` FOREIGN KEY (`profile_photo_evidence_id`) REFERENCES `evidence_document` (`id`),
  CONSTRAINT `professionals_profes_rate_type_id_f8be2161_fk_catalog_r` FOREIGN KEY (`rate_type_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_profes_registration_applica_104d17b6_fk_accounts_` FOREIGN KEY (`registration_application_id`) REFERENCES `accounts_registration_application` (`id`),
  CONSTRAINT `professionals_profes_self_declared_career_07ff4fb8_fk_catalog_r` FOREIGN KEY (`self_declared_career_stage_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `professionals_profes_tenant_id_fc5173e8_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `professionals_profes_user_id_aa86a34e_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `chk_professional_profile_completion_percent_range` CHECK (`completion_percent` >= 0 and `completion_percent` <= 100),
  CONSTRAINT `chk_professional_profile_notice_period_range` CHECK (`notice_period_days` is null or `notice_period_days` >= 0 and `notice_period_days` <= 365),
  CONSTRAINT `chk_professional_profile_rate_currency_required` CHECK (`expected_rate` is null or `rate_currency` <> ''),
  CONSTRAINT `chk_professional_profile_address_country_required` CHECK (`address_line_1` = '' and `address_line_2` = '' and `postal_code` = '' or `address_country_code` <> ''),
  CONSTRAINT `chk_professional_profile_classified_at_required` CHECK (`classification_status` <> 'CONFIRMED' or `classified_at` is not null),
  CONSTRAINT `chk_professional_profile_classified_by_not_owner` CHECK (`classified_by_id` <> `user_id` or `classified_by_id` is null)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professionals_professional_profile`
--

LOCK TABLES `professionals_professional_profile` WRITE;
/*!40000 ALTER TABLE `professionals_professional_profile` DISABLE KEYS */;
INSERT INTO `professionals_professional_profile` VALUES (1,'191a9422d8de41659558437851c3d1fb','2026-08-12 07:31:29.028850','2026-08-21 09:47:53.613753','APPROVED','CANDIDATE','CONFIRMED','2026-08-20 12:56:56.294402','',1,0.00,'Sharvani','Sharvani Kokkonda','Sharvani','','Kokkonda','','','2026-08-06','[\"India\", \"Pakisthan\"]','IN','karimnagar','Asia/Kolkata','','','','IN','sharvanikokkonda@gmail.com','+917567576567','','CLIENT_SPECIFIC','','','OG','test','[]','[]','USER',NULL,30,'[\"13\"]','[]',1,NULL,'','\"{\\\"helmet_size\\\":\\\"s\\\",\\\"safety_boot_size\\\":\\\"US 10\\\",\\\"coverall_size\\\":\\\"m\\\",\\\"additional_requirements\\\":\\\"Requirements\\\"}\"',NULL,NULL,21,2,1,26,NULL,4,18,14,2,23,1,NULL,1,3,'[]',0),(2,'a62a0c924593468bb758c2445f293265','2026-08-14 06:29:11.913238','2026-08-21 12:14:48.711290','STAGE2_SUBMITTED','UNCLASSIFIED','NOT_ASSESSED',NULL,'',3,0.00,'Myana Pavani','Pavani Myana','Pavani','','Myana','','Family-Given','2000-09-03','[\"Indian\"]','IN','Rajanna Sircilla','Asia/Kolkata','','','','IN','pavanimyana2000@gmail.com','+919676704365','','CLIENT_SPECIFIC','Junior Surveyor','1-3','OG','Professional Summary Professional Summary Professional Summary Professional Summary','[]','[]','USER','2026-09-01',NULL,'[\"13\"]','[\"Hyderabad\"]',1,NULL,'','\"{\\\"helmet_size\\\":\\\"m\\\",\\\"safety_boot_size\\\":\\\"UK 10\\\",\\\"coverall_size\\\":\\\"m\\\",\\\"additional_requirements\\\":\\\"\\\"}\"',NULL,NULL,19,NULL,3,26,NULL,1,18,1,4,25,2,NULL,1,6,'[]',0),(3,'ff164412f8f548bb97bb986d8f01d78f','2026-08-19 12:42:38.089939','2026-08-20 08:53:42.350312','STAGE1_COMPLETE','UNCLASSIFIED','NOT_ASSESSED',NULL,'',1,0.00,'','Raju Shanigarapu','Raju','','Shanigarapu','','Family-Given',NULL,'[]','IN','Hyderabad','Asia/Kolkata','','','','','','','','CLIENT_SPECIFIC','','1-3','','','[]','[]','USER',NULL,NULL,'[]','[]',0,NULL,'','{}',NULL,NULL,NULL,NULL,5,NULL,NULL,1,NULL,1,6,NULL,3,NULL,1,7,'[]',0);
/*!40000 ALTER TABLE `professionals_professional_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professionals_professional_review`
--

DROP TABLE IF EXISTS `professionals_professional_review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `professionals_professional_review` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `review_type` varchar(30) NOT NULL,
  `profile_version` int(10) unsigned NOT NULL CHECK (`profile_version` >= 0),
  `submitted_at` datetime(6) NOT NULL,
  `system_recommendation` varchar(20) NOT NULL,
  `system_confidence` decimal(5,2) DEFAULT NULL,
  `ruleset_version` varchar(30) NOT NULL,
  `previous_classification` varchar(20) NOT NULL,
  `proposed_classification` varchar(20) NOT NULL,
  `decision` varchar(20) NOT NULL,
  `final_classification` varchar(20) NOT NULL,
  `reviewer_role_snapshot` varchar(60) NOT NULL,
  `decision_reason` longtext NOT NULL,
  `reviewer_notes` longtext NOT NULL,
  `criteria_snapshot` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`criteria_snapshot`)),
  `decided_at` datetime(6) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `submitted_by_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `professionals_profes_professional_id_2c937419_fk_professio` (`professional_id`),
  KEY `professionals_profes_reviewed_by_id_895fe0d6_fk_accounts_` (`reviewed_by_id`),
  KEY `professionals_profes_submitted_by_id_0d754456_fk_accounts_` (`submitted_by_id`),
  KEY `professionals_profes_tenant_id_fb047833_fk_tenancy_t` (`tenant_id`),
  KEY `professionals_professional_review_created_at_c6b1617a` (`created_at`),
  KEY `professionals_professional_review_decision_f37a3792` (`decision`),
  CONSTRAINT `professionals_profes_professional_id_2c937419_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `professionals_profes_reviewed_by_id_895fe0d6_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `professionals_profes_submitted_by_id_0d754456_fk_accounts_` FOREIGN KEY (`submitted_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `professionals_profes_tenant_id_fb047833_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_professional_review_system_confidence_required` CHECK (`system_recommendation` = '' or `system_confidence` is not null),
  CONSTRAINT `chk_professional_review_ruleset_version_required` CHECK (`system_recommendation` = '' or `ruleset_version` <> ''),
  CONSTRAINT `chk_professional_review_final_classification_required` CHECK (`decision` <> 'APPROVED' or `final_classification` <> ''),
  CONSTRAINT `chk_professional_review_decided_at_required` CHECK (`decision` = 'PENDING' or `decided_at` is not null)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professionals_professional_review`
--

LOCK TABLES `professionals_professional_review` WRITE;
/*!40000 ALTER TABLE `professionals_professional_review` DISABLE KEYS */;
INSERT INTO `professionals_professional_review` VALUES (1,'2026-08-19 12:37:27.899828','PROFILE_APPROVAL',1,'2026-08-19 12:37:27.000000','',NULL,'','UNCLASSIFIED','','APPROVED','CANDIDATE','','test','','{}','2026-08-20 12:56:56.294402',1,2,3,1),(2,'2026-08-21 11:39:35.698472','PROFILE_APPROVAL',1,'2026-08-21 11:39:35.698158','',NULL,'','UNCLASSIFIED','','RETURNED','','','Enter proper Project Experience','Enter proper Project Experience','{}','2026-08-21 11:48:36.378636',2,6,6,1),(3,'2026-08-21 11:49:03.442953','PROFILE_APPROVAL',2,'2026-08-21 11:49:03.441830','',NULL,'','UNCLASSIFIED','','RETURNED','','','Please give client approval details','Please give client approval details','{}','2026-08-21 11:56:30.089294',2,6,6,1),(4,'2026-08-21 12:14:48.712321','PROFILE_APPROVAL',3,'2026-08-21 12:14:48.711006','',NULL,'','UNCLASSIFIED','','PENDING','','','','','{}',NULL,2,NULL,6,1);
/*!40000 ALTER TABLE `professionals_professional_review` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resumes_resume_generation`
--

DROP TABLE IF EXISTS `resumes_resume_generation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resumes_resume_generation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `status` varchar(30) NOT NULL,
  `source_snapshot` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`source_snapshot`)),
  `override_values` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`override_values`)),
  `consent_snapshot` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`consent_snapshot`)),
  `validation_result` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`validation_result`)),
  `output_storage_key` varchar(600) NOT NULL,
  `output_hash` varchar(128) NOT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `submitted_at` datetime(6) DEFAULT NULL,
  `generated_at` datetime(6) NOT NULL,
  `generated_by_id` bigint(20) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `supersedes_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `resume_template_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `resumes_resume_gener_generated_by_id_d9671ca8_fk_accounts_` (`generated_by_id`),
  KEY `resumes_resume_gener_professional_id_f5d8b951_fk_professio` (`professional_id`),
  KEY `resumes_resume_gener_reviewed_by_id_f20c680a_fk_accounts_` (`reviewed_by_id`),
  KEY `resumes_resume_gener_supersedes_id_20062fa8_fk_resumes_r` (`supersedes_id`),
  KEY `resumes_resume_gener_tenant_id_020e6390_fk_tenancy_t` (`tenant_id`),
  KEY `resumes_resume_gener_resume_template_id_a1fb6426_fk_resumes_r` (`resume_template_id`),
  KEY `resumes_resume_generation_status_42dbe5e1` (`status`),
  KEY `resumes_resume_generation_generated_at_2c489afa` (`generated_at`),
  CONSTRAINT `resumes_resume_gener_generated_by_id_d9671ca8_fk_accounts_` FOREIGN KEY (`generated_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `resumes_resume_gener_professional_id_f5d8b951_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `resumes_resume_gener_resume_template_id_a1fb6426_fk_resumes_r` FOREIGN KEY (`resume_template_id`) REFERENCES `resumes_resume_template` (`id`),
  CONSTRAINT `resumes_resume_gener_reviewed_by_id_f20c680a_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `resumes_resume_gener_supersedes_id_20062fa8_fk_resumes_r` FOREIGN KEY (`supersedes_id`) REFERENCES `resumes_resume_generation` (`id`),
  CONSTRAINT `resumes_resume_gener_tenant_id_020e6390_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_resume_generation_reviewed_at_required` CHECK (`status` <> 'APPROVED' or `reviewed_at` is not null),
  CONSTRAINT `chk_resume_generation_submitted_at_required` CHECK (`status` <> 'SUBMITTED' or `submitted_at` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resumes_resume_generation`
--

LOCK TABLES `resumes_resume_generation` WRITE;
/*!40000 ALTER TABLE `resumes_resume_generation` DISABLE KEYS */;
/*!40000 ALTER TABLE `resumes_resume_generation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resumes_resume_template`
--

DROP TABLE IF EXISTS `resumes_resume_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resumes_resume_template` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `template_code` varchar(60) NOT NULL,
  `template_name` varchar(180) NOT NULL,
  `version` varchar(30) NOT NULL,
  `output_type` varchar(20) NOT NULL,
  `template_storage_key` varchar(600) NOT NULL,
  `mapping_schema` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`mapping_schema`)),
  `required_fields_schema` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`required_fields_schema`)),
  `confidentiality_rules` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`confidentiality_rules`)),
  `status` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `published_at` datetime(6) DEFAULT NULL,
  `retired_at` datetime(6) DEFAULT NULL,
  `client_organization_id` bigint(20) DEFAULT NULL,
  `created_by_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_resume_template_tenant_client_code_version` (`tenant_id`,`client_organization_id`,`template_code`,`version`),
  KEY `resumes_resume_templ_client_organization__fa49b9a3_fk_tenancy_o` (`client_organization_id`),
  KEY `resumes_resume_templ_created_by_id_481c4ec0_fk_accounts_` (`created_by_id`),
  KEY `resumes_resume_template_created_at_7bf77baa` (`created_at`),
  KEY `resumes_resume_template_status_5419bd07` (`status`),
  CONSTRAINT `resumes_resume_templ_client_organization__fa49b9a3_fk_tenancy_o` FOREIGN KEY (`client_organization_id`) REFERENCES `tenancy_organization` (`id`),
  CONSTRAINT `resumes_resume_templ_created_by_id_481c4ec0_fk_accounts_` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `resumes_resume_template_tenant_id_f9a6b499_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_resume_template_published_at_required` CHECK (`status` <> 'PUBLISHED' or `published_at` is not null),
  CONSTRAINT `chk_resume_template_retired_at_required` CHECK (`status` <> 'RETIRED' or `retired_at` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resumes_resume_template`
--

LOCK TABLES `resumes_resume_template` WRITE;
/*!40000 ALTER TABLE `resumes_resume_template` DISABLE KEYS */;
/*!40000 ALTER TABLE `resumes_resume_template` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_candidate_consent`
--

DROP TABLE IF EXISTS `tenancy_candidate_consent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_candidate_consent` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `decision` varchar(15) NOT NULL,
  `fields` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`fields`)),
  `decided_at` datetime(6) NOT NULL,
  `withdrawn_at` datetime(6) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `disclosure_request_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_candidate_co_professional_id_473dc5aa_fk_professio` (`professional_id`),
  KEY `tenancy_candidate_co_disclosure_request_i_7dbe228b_fk_tenancy_d` (`disclosure_request_id`),
  CONSTRAINT `tenancy_candidate_co_disclosure_request_i_7dbe228b_fk_tenancy_d` FOREIGN KEY (`disclosure_request_id`) REFERENCES `tenancy_disclosure_request` (`id`),
  CONSTRAINT `tenancy_candidate_co_professional_id_473dc5aa_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_candidate_consent`
--

LOCK TABLES `tenancy_candidate_consent` WRITE;
/*!40000 ALTER TABLE `tenancy_candidate_consent` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_candidate_consent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_conflict_of_interest_declaration`
--

DROP TABLE IF EXISTS `tenancy_conflict_of_interest_declaration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_conflict_of_interest_declaration` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `has_conflict` tinyint(1) NOT NULL,
  `details` longtext NOT NULL,
  `mitigation` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `declared_by_id` bigint(20) NOT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `project_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_conflict_of__declared_by_id_62afb48d_fk_accounts_` (`declared_by_id`),
  KEY `tenancy_conflict_of__reviewed_by_id_0d555b77_fk_accounts_` (`reviewed_by_id`),
  KEY `tenancy_conflict_of__tenant_id_74703d09_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_conflict_of__project_id_7fcd3d00_fk_tenancy_p` (`project_id`),
  KEY `tenancy_conflict_of_interest_declaration_created_at_8a390425` (`created_at`),
  CONSTRAINT `tenancy_conflict_of__declared_by_id_62afb48d_fk_accounts_` FOREIGN KEY (`declared_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_conflict_of__project_id_7fcd3d00_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`),
  CONSTRAINT `tenancy_conflict_of__reviewed_by_id_0d555b77_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_conflict_of__tenant_id_74703d09_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_conflict_of_interest_declaration`
--

LOCK TABLES `tenancy_conflict_of_interest_declaration` WRITE;
/*!40000 ALTER TABLE `tenancy_conflict_of_interest_declaration` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_conflict_of_interest_declaration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_data_export_request`
--

DROP TABLE IF EXISTS `tenancy_data_export_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_data_export_request` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `purpose` longtext NOT NULL,
  `scope` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`scope`)),
  `status` varchar(20) NOT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `expiry_date` datetime(6) DEFAULT NULL,
  `watermark_applied` tinyint(1) NOT NULL,
  `approved_by_id` bigint(20) DEFAULT NULL,
  `requested_by_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_data_export__approved_by_id_a5678f63_fk_accounts_` (`approved_by_id`),
  KEY `tenancy_data_export__requested_by_id_d5681123_fk_accounts_` (`requested_by_id`),
  KEY `tenancy_data_export__tenant_id_ae0095fa_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_data_export_request_created_at_3c61e88c` (`created_at`),
  CONSTRAINT `tenancy_data_export__approved_by_id_a5678f63_fk_accounts_` FOREIGN KEY (`approved_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_data_export__requested_by_id_d5681123_fk_accounts_` FOREIGN KEY (`requested_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_data_export__tenant_id_ae0095fa_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_data_export_request`
--

LOCK TABLES `tenancy_data_export_request` WRITE;
/*!40000 ALTER TABLE `tenancy_data_export_request` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_data_export_request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_disclosure_request`
--

DROP TABLE IF EXISTS `tenancy_disclosure_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_disclosure_request` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `requested_fields` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`requested_fields`)),
  `purpose` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `requested_by_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `project_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_disclosure_r_project_id_d32f14d2_fk_tenancy_p` (`project_id`),
  KEY `tenancy_disclosure_r_professional_id_28162be7_fk_professio` (`professional_id`),
  KEY `tenancy_disclosure_r_requested_by_id_766b712f_fk_accounts_` (`requested_by_id`),
  KEY `tenancy_disclosure_r_tenant_id_8ffec9a4_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_disclosure_request_created_at_5803d17a` (`created_at`),
  CONSTRAINT `tenancy_disclosure_r_professional_id_28162be7_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `tenancy_disclosure_r_project_id_d32f14d2_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`),
  CONSTRAINT `tenancy_disclosure_r_requested_by_id_766b712f_fk_accounts_` FOREIGN KEY (`requested_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_disclosure_r_tenant_id_8ffec9a4_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_disclosure_request`
--

LOCK TABLES `tenancy_disclosure_request` WRITE;
/*!40000 ALTER TABLE `tenancy_disclosure_request` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_disclosure_request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_module`
--

DROP TABLE IF EXISTS `tenancy_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_module` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `code` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `tenancy_module_created_at_39057e23` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_module`
--

LOCK TABLES `tenancy_module` WRITE;
/*!40000 ALTER TABLE `tenancy_module` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_organization`
--

DROP TABLE IF EXISTS `tenancy_organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_organization` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `organization_type` varchar(40) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `legal_name` varchar(250) DEFAULT NULL,
  `code` varchar(60) DEFAULT NULL,
  `country_code` varchar(2) DEFAULT NULL,
  `city` varchar(120) DEFAULT NULL,
  `website` varchar(500) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `external_reference` varchar(100) DEFAULT NULL,
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata`)),
  `is_active` tinyint(1) NOT NULL,
  `industry_id` bigint(20) DEFAULT NULL,
  `parent_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `legal_entity_id` bigint(20) DEFAULT NULL,
  `owner_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_organization_industry_id_384c20b3_fk_catalog_r` (`industry_id`),
  KEY `tenancy_organization_parent_id_d941f207_fk_tenancy_o` (`parent_id`),
  KEY `tenancy_organization_tenant_id_2faac137_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `tenancy_organization_created_at_fc5e9a21` (`created_at`),
  KEY `tenancy_organization_external_reference_fb95bf47` (`external_reference`),
  KEY `tenancy_organization_legal_entity_id_adf560be_fk_tenancy_t` (`legal_entity_id`),
  KEY `tenancy_organization_owner_id_a4cc9f7a_fk_accounts_user_id` (`owner_id`),
  CONSTRAINT `tenancy_organization_industry_id_384c20b3_fk_catalog_r` FOREIGN KEY (`industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `tenancy_organization_legal_entity_id_adf560be_fk_tenancy_t` FOREIGN KEY (`legal_entity_id`) REFERENCES `tenancy_tenant_legal_entity` (`id`),
  CONSTRAINT `tenancy_organization_owner_id_a4cc9f7a_fk_accounts_user_id` FOREIGN KEY (`owner_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_organization_parent_id_d941f207_fk_tenancy_o` FOREIGN KEY (`parent_id`) REFERENCES `tenancy_organization` (`id`),
  CONSTRAINT `tenancy_organization_tenant_id_2faac137_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_organization`
--

LOCK TABLES `tenancy_organization` WRITE;
/*!40000 ALTER TABLE `tenancy_organization` DISABLE KEYS */;
INSERT INTO `tenancy_organization` VALUES (2,'632aa5b060d542639e679cea39f15650','2026-08-25 09:53:47.849612','2026-08-25 10:26:53.177578','OPERATING_UNIT','A2Z Ships','A2Z','ORG001','IN','Mumbai','https://www.abc.com','a2z@gmail.com','Reference','{}',1,1,NULL,3,NULL,NULL);
/*!40000 ALTER TABLE `tenancy_organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_project`
--

DROP TABLE IF EXISTS `tenancy_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_project` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `project_code` varchar(50) NOT NULL,
  `project_name` varchar(250) NOT NULL,
  `project_type` varchar(100) NOT NULL,
  `country_code` varchar(2) NOT NULL,
  `city` varchar(120) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `confidentiality_classification` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `description` longtext NOT NULL,
  `client_organization_id` bigint(20) DEFAULT NULL,
  `industry_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `business_unit_id` bigint(20) DEFAULT NULL,
  `location_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_project_code_per_tenant` (`tenant_id`,`project_code`),
  KEY `tenancy_project_location_id_6376e1a3_fk_tenancy_t` (`location_id`),
  KEY `tenancy_project_client_organization__a781f185_fk_tenancy_o` (`client_organization_id`),
  KEY `tenancy_project_industry_id_7f4b4783_fk_catalog_r` (`industry_id`),
  KEY `tenancy_project_created_at_9a08ba45` (`created_at`),
  KEY `tenancy_project_business_unit_id_24c73da0_fk_tenancy_o` (`business_unit_id`),
  CONSTRAINT `tenancy_project_business_unit_id_24c73da0_fk_tenancy_o` FOREIGN KEY (`business_unit_id`) REFERENCES `tenancy_organization` (`id`),
  CONSTRAINT `tenancy_project_client_organization__a781f185_fk_tenancy_o` FOREIGN KEY (`client_organization_id`) REFERENCES `tenancy_organization` (`id`),
  CONSTRAINT `tenancy_project_industry_id_7f4b4783_fk_catalog_r` FOREIGN KEY (`industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `tenancy_project_location_id_6376e1a3_fk_tenancy_t` FOREIGN KEY (`location_id`) REFERENCES `tenancy_tenant_location` (`id`),
  CONSTRAINT `tenancy_project_tenant_id_8d43cb8c_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_project`
--

LOCK TABLES `tenancy_project` WRITE;
/*!40000 ALTER TABLE `tenancy_project` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_project_candidate`
--

DROP TABLE IF EXISTS `tenancy_project_candidate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_project_candidate` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `shortlist_status` varchar(30) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  `project_id` bigint(20) NOT NULL,
  `shortlisted_by_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_project_candidate` (`project_id`,`professional_id`),
  KEY `tenancy_project_cand_professional_id_2c4d7f1f_fk_professio` (`professional_id`),
  KEY `tenancy_project_cand_shortlisted_by_id_87bcc8b8_fk_accounts_` (`shortlisted_by_id`),
  CONSTRAINT `tenancy_project_cand_professional_id_2c4d7f1f_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `tenancy_project_cand_project_id_1e58a749_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`),
  CONSTRAINT `tenancy_project_cand_shortlisted_by_id_87bcc8b8_fk_accounts_` FOREIGN KEY (`shortlisted_by_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_project_candidate`
--

LOCK TABLES `tenancy_project_candidate` WRITE;
/*!40000 ALTER TABLE `tenancy_project_candidate` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_project_candidate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_project_membership`
--

DROP TABLE IF EXISTS `tenancy_project_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_project_membership` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `scopes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`scopes`)),
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `entitlement` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`entitlement`)),
  `assigned_by_id` bigint(20) NOT NULL,
  `project_id` bigint(20) NOT NULL,
  `role_id` bigint(20) NOT NULL,
  `membership_id` bigint(20) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_project_membership` (`project_id`,`membership_id`),
  KEY `tenancy_project_memb_assigned_by_id_06606046_fk_accounts_` (`assigned_by_id`),
  KEY `tenancy_project_membership_role_id_c4946bc8_fk_accounts_roles_id` (`role_id`),
  KEY `tenancy_project_memb_membership_id_294d8a62_fk_tenancy_t` (`membership_id`),
  KEY `tenancy_project_membership_user_id_31f502bf_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `tenancy_project_memb_assigned_by_id_06606046_fk_accounts_` FOREIGN KEY (`assigned_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_project_memb_membership_id_294d8a62_fk_tenancy_t` FOREIGN KEY (`membership_id`) REFERENCES `tenancy_tenant_membership` (`id`),
  CONSTRAINT `tenancy_project_memb_project_id_57e05ff7_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`),
  CONSTRAINT `tenancy_project_membership_role_id_c4946bc8_fk_accounts_roles_id` FOREIGN KEY (`role_id`) REFERENCES `accounts_roles` (`id`),
  CONSTRAINT `tenancy_project_membership_user_id_31f502bf_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_project_membership`
--

LOCK TABLES `tenancy_project_membership` WRITE;
/*!40000 ALTER TABLE `tenancy_project_membership` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_project_membership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_project_placement`
--

DROP TABLE IF EXISTS `tenancy_project_placement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_project_placement` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `assigned_role` varchar(120) NOT NULL,
  `deployment_start` date NOT NULL,
  `deployment_end` date DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `professional_id` bigint(20) NOT NULL,
  `professional_assignment_id` bigint(20) DEFAULT NULL,
  `project_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_project_plac_professional_id_b77a00c3_fk_professio` (`professional_id`),
  KEY `tenancy_project_plac_professional_assignm_cf22321f_fk_experienc` (`professional_assignment_id`),
  KEY `tenancy_project_plac_project_id_ae914050_fk_tenancy_p` (`project_id`),
  CONSTRAINT `tenancy_project_plac_professional_assignm_cf22321f_fk_experienc` FOREIGN KEY (`professional_assignment_id`) REFERENCES `experience_professional_assignment` (`id`),
  CONSTRAINT `tenancy_project_plac_professional_id_b77a00c3_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `tenancy_project_plac_project_id_ae914050_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_project_placement`
--

LOCK TABLES `tenancy_project_placement` WRITE;
/*!40000 ALTER TABLE `tenancy_project_placement` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_project_placement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_project_requirement`
--

DROP TABLE IF EXISTS `tenancy_project_requirement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_project_requirement` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `required_count` int(10) unsigned NOT NULL CHECK (`required_count` >= 0),
  `minimum_experience_years` decimal(5,2) NOT NULL,
  `is_mandatory` tinyint(1) NOT NULL,
  `remarks` longtext NOT NULL,
  `project_id` bigint(20) NOT NULL,
  `role_code_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_project_requ_project_id_d670b771_fk_tenancy_p` (`project_id`),
  KEY `tenancy_project_requ_role_code_id_e32aa060_fk_catalog_r` (`role_code_id`),
  CONSTRAINT `tenancy_project_requ_project_id_d670b771_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`),
  CONSTRAINT `tenancy_project_requ_role_code_id_e32aa060_fk_catalog_r` FOREIGN KEY (`role_code_id`) REFERENCES `catalog_reference_value` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_project_requirement`
--

LOCK TABLES `tenancy_project_requirement` WRITE;
/*!40000 ALTER TABLE `tenancy_project_requirement` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_project_requirement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_project_requirement_scope`
--

DROP TABLE IF EXISTS `tenancy_project_requirement_scope`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_project_requirement_scope` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `requirement_id` bigint(20) NOT NULL,
  `scope_catalog_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_requirement_scope` (`requirement_id`,`scope_catalog_id`),
  KEY `tenancy_project_requ_scope_catalog_id_9037deb9_fk_catalog_s` (`scope_catalog_id`),
  CONSTRAINT `tenancy_project_requ_requirement_id_a3b6ac97_fk_tenancy_p` FOREIGN KEY (`requirement_id`) REFERENCES `tenancy_project_requirement` (`id`),
  CONSTRAINT `tenancy_project_requ_scope_catalog_id_9037deb9_fk_catalog_s` FOREIGN KEY (`scope_catalog_id`) REFERENCES `catalog_scope_catalog` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_project_requirement_scope`
--

LOCK TABLES `tenancy_project_requirement_scope` WRITE;
/*!40000 ALTER TABLE `tenancy_project_requirement_scope` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_project_requirement_scope` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_project_scope_catalog_entries`
--

DROP TABLE IF EXISTS `tenancy_project_scope_catalog_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_project_scope_catalog_entries` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `project_id` bigint(20) NOT NULL,
  `scopecatalog_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tenancy_project_scope_ca_project_id_scopecatalog__be5cafbe_uniq` (`project_id`,`scopecatalog_id`),
  KEY `tenancy_project_scop_scopecatalog_id_fd6e1b14_fk_catalog_s` (`scopecatalog_id`),
  CONSTRAINT `tenancy_project_scop_project_id_42c9eef0_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`),
  CONSTRAINT `tenancy_project_scop_scopecatalog_id_fd6e1b14_fk_catalog_s` FOREIGN KEY (`scopecatalog_id`) REFERENCES `catalog_scope_catalog` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_project_scope_catalog_entries`
--

LOCK TABLES `tenancy_project_scope_catalog_entries` WRITE;
/*!40000 ALTER TABLE `tenancy_project_scope_catalog_entries` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_project_scope_catalog_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_project_scope_link`
--

DROP TABLE IF EXISTS `tenancy_project_scope_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_project_scope_link` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `allocation_percent` smallint(5) unsigned NOT NULL CHECK (`allocation_percent` >= 0),
  `verified_field_days` int(10) unsigned DEFAULT NULL CHECK (`verified_field_days` >= 0),
  `authority_action_code_id` bigint(20) NOT NULL,
  `experience_project_scope_id` bigint(20) DEFAULT NULL,
  `industry_id` bigint(20) NOT NULL,
  `placement_id` bigint(20) DEFAULT NULL,
  `professional_id` bigint(20) NOT NULL,
  `project_id` bigint(20) NOT NULL,
  `scope_catalog_id` bigint(20) NOT NULL,
  `evidence_document_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_project_scope_link` (`project_id`,`professional_id`,`scope_catalog_id`),
  KEY `tenancy_project_scop_authority_action_cod_d0fbbfae_fk_catalog_r` (`authority_action_code_id`),
  KEY `tenancy_project_scop_experience_project_s_e37b9791_fk_experienc` (`experience_project_scope_id`),
  KEY `tenancy_project_scop_industry_id_d9bd6236_fk_catalog_r` (`industry_id`),
  KEY `tenancy_project_scop_placement_id_57c19805_fk_tenancy_p` (`placement_id`),
  KEY `tenancy_project_scop_professional_id_156866b8_fk_professio` (`professional_id`),
  KEY `tenancy_project_scop_scope_catalog_id_ac7c3309_fk_catalog_s` (`scope_catalog_id`),
  KEY `tenancy_project_scop_evidence_document_id_e93b454a_fk_tenancy_t` (`evidence_document_id`),
  KEY `tenancy_project_scope_link_created_at_7a7098b0` (`created_at`),
  CONSTRAINT `tenancy_project_scop_authority_action_cod_d0fbbfae_fk_catalog_r` FOREIGN KEY (`authority_action_code_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `tenancy_project_scop_evidence_document_id_e93b454a_fk_tenancy_t` FOREIGN KEY (`evidence_document_id`) REFERENCES `tenancy_tenant_document` (`id`),
  CONSTRAINT `tenancy_project_scop_experience_project_s_e37b9791_fk_experienc` FOREIGN KEY (`experience_project_scope_id`) REFERENCES `experience_project_scope` (`id`),
  CONSTRAINT `tenancy_project_scop_industry_id_d9bd6236_fk_catalog_r` FOREIGN KEY (`industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `tenancy_project_scop_placement_id_57c19805_fk_tenancy_p` FOREIGN KEY (`placement_id`) REFERENCES `tenancy_project_placement` (`id`),
  CONSTRAINT `tenancy_project_scop_professional_id_156866b8_fk_professio` FOREIGN KEY (`professional_id`) REFERENCES `professionals_professional_profile` (`id`),
  CONSTRAINT `tenancy_project_scop_project_id_bc758ff6_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`),
  CONSTRAINT `tenancy_project_scop_scope_catalog_id_ac7c3309_fk_catalog_s` FOREIGN KEY (`scope_catalog_id`) REFERENCES `catalog_scope_catalog` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_project_scope_link`
--

LOCK TABLES `tenancy_project_scope_link` WRITE;
/*!40000 ALTER TABLE `tenancy_project_scope_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_project_scope_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant`
--

DROP TABLE IF EXISTS `tenancy_tenant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `name` varchar(200) DEFAULT NULL,
  `legal_name` varchar(250) DEFAULT NULL,
  `code` varchar(50) DEFAULT NULL,
  `portal_slug` varchar(80) DEFAULT NULL,
  `custom_domain` varchar(255) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `registration_enabled` tinyint(1) NOT NULL,
  `login_enabled` tinyint(1) NOT NULL,
  `default_timezone` varchar(64) DEFAULT NULL,
  `default_currency` varchar(3) DEFAULT NULL,
  `contact_email` varchar(254) DEFAULT NULL,
  `contact_phone` varchar(20) DEFAULT NULL,
  `settings` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`settings`)),
  `branding` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`branding`)),
  `logo` varchar(1000) DEFAULT NULL,
  `created_by_id` bigint(20) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `organisation_type` varchar(30) DEFAULT NULL,
  `parent_tenant_id` bigint(20) DEFAULT NULL,
  `service_scope_ids` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`service_scope_ids`)),
  `status_reason` longtext DEFAULT NULL,
  `trade_name` varchar(200) DEFAULT NULL,
  `website` varchar(500) DEFAULT NULL,
  `workspace_type` varchar(20) DEFAULT NULL,
  `industry_ids` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`industry_ids`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `code` (`code`),
  UNIQUE KEY `portal_slug` (`portal_slug`),
  UNIQUE KEY `custom_domain` (`custom_domain`),
  KEY `tenancy_tenant_created_at_8f2ee9aa` (`created_at`),
  KEY `tenancy_tenant_status_bb1f1bbe` (`status`),
  KEY `tenancy_tenant_parent_tenant_id_2d45502a_fk_tenancy_tenant_id` (`parent_tenant_id`),
  KEY `tenancy_tenant_created_by_id_0a6fcbbc_fk_accounts_user_id` (`created_by_id`),
  CONSTRAINT `tenancy_tenant_created_by_id_0a6fcbbc_fk_accounts_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_parent_tenant_id_2d45502a_fk_tenancy_tenant_id` FOREIGN KEY (`parent_tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant`
--

LOCK TABLES `tenancy_tenant` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant` DISABLE KEYS */;
INSERT INTO `tenancy_tenant` VALUES (1,'5c6c4a0ee501446f993acb448d4cbb2c','2026-08-12 07:05:41.893134','2026-08-12 07:05:41.893169','OceanStar','OceanStar','OCEAN','oceanstar','http://localhost:3000/oceanstar/','ACTIVE',1,1,'Asia/Kolkata','INR','','','{}','{}','',1,NULL,NULL,NULL,'[]',NULL,NULL,NULL,NULL,'[]'),(3,'068cdad39c8949a1b2a905bac905195b','2026-08-25 07:55:51.808006','2026-08-26 08:14:21.740776','A2Z Ships Banglore','A2Z','A2Z','a2z','http://localhost:3000/a2z/','PENDING',1,1,'Asia/Kolkata','INR','a2z@gmail.com','+919676704365','{}','{}','a2z-ships-banglore/a2z-ships-banglore_docs/pavan_image.jpg',1,'A2Z Ships A2Z Ships A2Z Ships A2Z Ships','PMC',NULL,'1',NULL,'A','https://www.abc.com','PERSONAL','[]');
/*!40000 ALTER TABLE `tenancy_tenant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_approval_matrix`
--

DROP TABLE IF EXISTS `tenancy_tenant_approval_matrix`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_approval_matrix` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `document_type` varchar(20) NOT NULL,
  `sequence` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`sequence`)),
  `project_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_appro_project_id_8a7003db_fk_tenancy_p` (`project_id`),
  KEY `tenancy_tenant_appro_tenant_id_8b6039da_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_approval_matrix_created_at_d0d9d64f` (`created_at`),
  CONSTRAINT `tenancy_tenant_appro_project_id_8a7003db_fk_tenancy_p` FOREIGN KEY (`project_id`) REFERENCES `tenancy_project` (`id`),
  CONSTRAINT `tenancy_tenant_appro_tenant_id_8b6039da_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_approval_matrix`
--

LOCK TABLES `tenancy_tenant_approval_matrix` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_approval_matrix` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_approval_matrix` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_authorised_representative`
--

DROP TABLE IF EXISTS `tenancy_tenant_authorised_representative`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_authorised_representative` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `title` varchar(100) NOT NULL,
  `official_email` varchar(254) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `authority_type` varchar(30) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `verification_status` varchar(30) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `evidence_document_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_autho_tenant_id_07a2eeae_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_autho_user_id_76a4100d_fk_accounts_` (`user_id`),
  KEY `tenancy_tenant_autho_evidence_document_id_4dad6f4b_fk_tenancy_t` (`evidence_document_id`),
  KEY `tenancy_tenant_authorised_representative_created_at_3bb3035c` (`created_at`),
  CONSTRAINT `tenancy_tenant_autho_evidence_document_id_4dad6f4b_fk_tenancy_t` FOREIGN KEY (`evidence_document_id`) REFERENCES `tenancy_tenant_document` (`id`),
  CONSTRAINT `tenancy_tenant_autho_tenant_id_07a2eeae_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `tenancy_tenant_autho_user_id_76a4100d_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_authorised_representative`
--

LOCK TABLES `tenancy_tenant_authorised_representative` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_authorised_representative` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_authorised_representative` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_billing`
--

DROP TABLE IF EXISTS `tenancy_tenant_billing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_billing` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `po_required` tinyint(1) NOT NULL,
  `po_format` varchar(100) NOT NULL,
  `po_contact` varchar(255) NOT NULL,
  `payment_terms` varchar(100) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `billing_entity_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tenant_id` (`tenant_id`),
  KEY `tenancy_tenant_billi_billing_entity_id_7058ae56_fk_tenancy_t` (`billing_entity_id`),
  CONSTRAINT `tenancy_tenant_billi_billing_entity_id_7058ae56_fk_tenancy_t` FOREIGN KEY (`billing_entity_id`) REFERENCES `tenancy_tenant_legal_entity` (`id`),
  CONSTRAINT `tenancy_tenant_billing_tenant_id_5a4560dc_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_billing`
--

LOCK TABLES `tenancy_tenant_billing` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_billing` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_billing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_branding`
--

DROP TABLE IF EXISTS `tenancy_tenant_branding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_branding` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `logo` varchar(1000) DEFAULT NULL,
  `colours` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`colours`)),
  `report_header` longtext NOT NULL,
  `report_footer` longtext NOT NULL,
  `disclaimer_text` longtext NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `tenancy_tenant_branding_tenant_id_8524c451_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_branding`
--

LOCK TABLES `tenancy_tenant_branding` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_branding` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_branding` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_business_unit`
--

DROP TABLE IF EXISTS `tenancy_tenant_business_unit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_business_unit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `code` varchar(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_business_unit_code` (`tenant_id`,`code`),
  KEY `tenancy_tenant_business_unit_created_at_5c00dd93` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_business_unit`
--

LOCK TABLES `tenancy_tenant_business_unit` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_business_unit` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_business_unit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_contact`
--

DROP TABLE IF EXISTS `tenancy_tenant_contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_contact` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `contact_type` varchar(20) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_contact_tenant_id_f1be50c7_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `tenancy_tenant_contact_user_id_574d372c_fk_accounts_user_id` (`user_id`),
  KEY `tenancy_tenant_contact_created_at_cbaf4bd6` (`created_at`),
  CONSTRAINT `tenancy_tenant_contact_tenant_id_f1be50c7_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `tenancy_tenant_contact_user_id_574d372c_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_contact`
--

LOCK TABLES `tenancy_tenant_contact` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_contact` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_document`
--

DROP TABLE IF EXISTS `tenancy_tenant_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_document` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `archived_at` datetime(6) DEFAULT NULL,
  `document_type` varchar(20) NOT NULL,
  `file` varchar(1000) NOT NULL,
  `file_hash` varchar(128) NOT NULL,
  `issue_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `remarks` longtext NOT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `superseded_by_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_docum_reviewed_by_id_63f2de4f_fk_accounts_` (`reviewed_by_id`),
  KEY `tenancy_tenant_docum_superseded_by_id_dd87abee_fk_tenancy_t` (`superseded_by_id`),
  KEY `tenancy_tenant_document_tenant_id_2e626d29_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `tenancy_tenant_document_created_at_7ae771f7` (`created_at`),
  KEY `tenancy_tenant_document_archived_at_d063de24` (`archived_at`),
  CONSTRAINT `tenancy_tenant_docum_reviewed_by_id_63f2de4f_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_docum_superseded_by_id_dd87abee_fk_tenancy_t` FOREIGN KEY (`superseded_by_id`) REFERENCES `tenancy_tenant_document` (`id`),
  CONSTRAINT `tenancy_tenant_document_tenant_id_2e626d29_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_document`
--

LOCK TABLES `tenancy_tenant_document` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_document` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_domain`
--

DROP TABLE IF EXISTS `tenancy_tenant_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_domain` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `verification_status` varchar(20) NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_tenant_domain` (`tenant_id`,`domain`),
  KEY `tenancy_tenant_domain_created_at_6c03a34a` (`created_at`),
  CONSTRAINT `tenancy_tenant_domain_tenant_id_35e3ef2f_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_domain`
--

LOCK TABLES `tenancy_tenant_domain` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_domain` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_domain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_industry`
--

DROP TABLE IF EXISTS `tenancy_tenant_industry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_industry` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `industry_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_tenant_industry` (`tenant_id`,`industry_id`),
  KEY `tenancy_tenant_indus_industry_id_5fbdb48a_fk_catalog_r` (`industry_id`),
  KEY `tenancy_tenant_industry_created_at_5f6f8de8` (`created_at`),
  CONSTRAINT `tenancy_tenant_indus_industry_id_5fbdb48a_fk_catalog_r` FOREIGN KEY (`industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `tenancy_tenant_industry_tenant_id_d4479f1b_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_industry`
--

LOCK TABLES `tenancy_tenant_industry` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_industry` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_industry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_integration`
--

DROP TABLE IF EXISTS `tenancy_tenant_integration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_integration` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `integration_type` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL,
  `secret_reference` text NOT NULL,
  `scopes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`scopes`)),
  `rotated_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_integ_tenant_id_2a2e402b_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_integration_created_at_ff73cede` (`created_at`),
  CONSTRAINT `tenancy_tenant_integ_tenant_id_2a2e402b_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_integration`
--

LOCK TABLES `tenancy_tenant_integration` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_integration` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_integration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_invitation`
--

DROP TABLE IF EXISTS `tenancy_tenant_invitation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_invitation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `token` varchar(255) NOT NULL,
  `status` varchar(20) NOT NULL,
  `sent_at` datetime(6) NOT NULL,
  `accepted_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `role_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `tenancy_tenant_invitation_role_id_4c1f8621_fk_accounts_roles_id` (`role_id`),
  KEY `tenancy_tenant_invit_tenant_id_dce797ea_fk_tenancy_t` (`tenant_id`),
  CONSTRAINT `tenancy_tenant_invit_tenant_id_dce797ea_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `tenancy_tenant_invitation_role_id_4c1f8621_fk_accounts_roles_id` FOREIGN KEY (`role_id`) REFERENCES `accounts_roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_invitation`
--

LOCK TABLES `tenancy_tenant_invitation` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_invitation` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_invitation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_ip_restriction`
--

DROP TABLE IF EXISTS `tenancy_tenant_ip_restriction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_ip_restriction` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `cidr_range` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `security_settings_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_ip_re_security_settings_id_e9ff412f_fk_tenancy_t` (`security_settings_id`),
  CONSTRAINT `tenancy_tenant_ip_re_security_settings_id_e9ff412f_fk_tenancy_t` FOREIGN KEY (`security_settings_id`) REFERENCES `tenancy_tenant_security_settings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_ip_restriction`
--

LOCK TABLES `tenancy_tenant_ip_restriction` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_ip_restriction` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_ip_restriction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_legal_acceptance`
--

DROP TABLE IF EXISTS `tenancy_tenant_legal_acceptance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_legal_acceptance` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `acceptance_type` varchar(10) NOT NULL,
  `version` varchar(50) NOT NULL,
  `jurisdiction` varchar(100) NOT NULL,
  `accepted_by_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_legal_accepted_by_id_06934b99_fk_accounts_` (`accepted_by_id`),
  KEY `tenancy_tenant_legal_tenant_id_74cb8dcf_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_legal_acceptance_created_at_aee7c73b` (`created_at`),
  CONSTRAINT `tenancy_tenant_legal_accepted_by_id_06934b99_fk_accounts_` FOREIGN KEY (`accepted_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_legal_tenant_id_74cb8dcf_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_legal_acceptance`
--

LOCK TABLES `tenancy_tenant_legal_acceptance` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_legal_acceptance` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_legal_acceptance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_legal_entity`
--

DROP TABLE IF EXISTS `tenancy_tenant_legal_entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_legal_entity` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `registration_number` text NOT NULL,
  `country_of_incorporation` varchar(2) NOT NULL,
  `incorporation_date` date DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `rejection_reason` longtext NOT NULL,
  `requested_by_id` bigint(20) DEFAULT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_legal_tenant_id_6f1a9ad8_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_legal_entity_created_at_8cafaf1f` (`created_at`),
  KEY `tenancy_tenant_legal_requested_by_id_b2b89273_fk_accounts_` (`requested_by_id`),
  KEY `tenancy_tenant_legal_reviewed_by_id_d1671cee_fk_accounts_` (`reviewed_by_id`),
  CONSTRAINT `tenancy_tenant_legal_requested_by_id_b2b89273_fk_accounts_` FOREIGN KEY (`requested_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_legal_reviewed_by_id_d1671cee_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_legal_tenant_id_6f1a9ad8_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_legal_entity`
--

LOCK TABLES `tenancy_tenant_legal_entity` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_legal_entity` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_legal_entity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_legal_settings`
--

DROP TABLE IF EXISTS `tenancy_tenant_legal_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_legal_settings` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nda_requirement` varchar(20) NOT NULL,
  `default_classification` varchar(20) NOT NULL,
  `retention_policy` varchar(100) NOT NULL,
  `is_legal_hold` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `tenancy_tenant_legal_tenant_id_f4ae0bd1_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_legal_settings`
--

LOCK TABLES `tenancy_tenant_legal_settings` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_legal_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_legal_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_location`
--

DROP TABLE IF EXISTS `tenancy_tenant_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_location` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `location_type` varchar(20) NOT NULL,
  `location_code` varchar(100) NOT NULL,
  `address_line1` varchar(255) NOT NULL,
  `address_line2` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `postal_code` varchar(20) NOT NULL,
  `country_code` varchar(2) NOT NULL,
  `timezone` varchar(64) NOT NULL,
  `latitude` decimal(9,6) DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  `is_head_office` tinyint(1) NOT NULL,
  `is_default_billing` tinyint(1) NOT NULL,
  `is_default_project_location` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `business_unit_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_location_tenant_id_ede5d92d_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `tenancy_tenant_location_created_at_b33bbaf1` (`created_at`),
  KEY `tenancy_tenant_locat_business_unit_id_047f9711_fk_tenancy_o` (`business_unit_id`),
  CONSTRAINT `tenancy_tenant_locat_business_unit_id_047f9711_fk_tenancy_o` FOREIGN KEY (`business_unit_id`) REFERENCES `tenancy_organization` (`id`),
  CONSTRAINT `tenancy_tenant_location_tenant_id_ede5d92d_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_location`
--

LOCK TABLES `tenancy_tenant_location` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_location` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_location` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_membership`
--

DROP TABLE IF EXISTS `tenancy_tenant_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_membership` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `status` varchar(10) NOT NULL,
  `joined_at` datetime(6) DEFAULT NULL,
  `left_at` datetime(6) DEFAULT NULL,
  `last_active_at` datetime(6) DEFAULT NULL,
  `invited_by_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_tenant_membership` (`tenant_id`,`user_id`),
  KEY `tenancy_tenant_membe_invited_by_id_602b1483_fk_accounts_` (`invited_by_id`),
  KEY `tenancy_tenant_membership_user_id_f5396e3b_fk_accounts_user_id` (`user_id`),
  KEY `tenancy_tenant_membership_created_at_f9bd1607` (`created_at`),
  CONSTRAINT `tenancy_tenant_membe_invited_by_id_602b1483_fk_accounts_` FOREIGN KEY (`invited_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_membe_tenant_id_c71119b8_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `tenancy_tenant_membership_user_id_f5396e3b_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_membership`
--

LOCK TABLES `tenancy_tenant_membership` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_membership` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_membership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_module_entitlement`
--

DROP TABLE IF EXISTS `tenancy_tenant_module_entitlement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_module_entitlement` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `status` varchar(20) NOT NULL,
  `limits` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`limits`)),
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `module_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_tenant_module` (`tenant_id`,`module_id`),
  KEY `tenancy_tenant_modul_module_id_04689e92_fk_tenancy_m` (`module_id`),
  KEY `tenancy_tenant_module_entitlement_created_at_c7f632c3` (`created_at`),
  CONSTRAINT `tenancy_tenant_modul_module_id_04689e92_fk_tenancy_m` FOREIGN KEY (`module_id`) REFERENCES `tenancy_module` (`id`),
  CONSTRAINT `tenancy_tenant_modul_tenant_id_b0b801c9_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_module_entitlement`
--

LOCK TABLES `tenancy_tenant_module_entitlement` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_module_entitlement` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_module_entitlement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_nda`
--

DROP TABLE IF EXISTS `tenancy_tenant_nda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_nda` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `version` varchar(50) NOT NULL,
  `parties` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`parties`)),
  `signatories` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`signatories`)),
  `effective_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `evidence_document_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_nda_evidence_document_id_4d0a3800_fk_tenancy_t` (`evidence_document_id`),
  KEY `tenancy_tenant_nda_tenant_id_568df7e4_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `tenancy_tenant_nda_created_at_c448f116` (`created_at`),
  CONSTRAINT `tenancy_tenant_nda_evidence_document_id_4d0a3800_fk_tenancy_t` FOREIGN KEY (`evidence_document_id`) REFERENCES `tenancy_tenant_document` (`id`),
  CONSTRAINT `tenancy_tenant_nda_tenant_id_568df7e4_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_nda`
--

LOCK TABLES `tenancy_tenant_nda` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_nda` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_nda` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_notification_settings`
--

DROP TABLE IF EXISTS `tenancy_tenant_notification_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_notification_settings` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `event_type` varchar(100) NOT NULL,
  `channels` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`channels`)),
  `escalation_rules` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`escalation_rules`)),
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_notif_tenant_id_d0cf462c_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_notification_settings_created_at_fc0446b7` (`created_at`),
  CONSTRAINT `tenancy_tenant_notif_tenant_id_d0cf462c_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_notification_settings`
--

LOCK TABLES `tenancy_tenant_notification_settings` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_notification_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_notification_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_numbering_config`
--

DROP TABLE IF EXISTS `tenancy_tenant_numbering_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_numbering_config` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `document_type` varchar(30) NOT NULL,
  `pattern` varchar(100) NOT NULL,
  `current_sequence` int(10) unsigned NOT NULL CHECK (`current_sequence` >= 0),
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_tenant_numbering` (`tenant_id`,`document_type`),
  CONSTRAINT `tenancy_tenant_numbe_tenant_id_db210d42_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_numbering_config`
--

LOCK TABLES `tenancy_tenant_numbering_config` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_numbering_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_numbering_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_operation`
--

DROP TABLE IF EXISTS `tenancy_tenant_operation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_operation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `country_code` varchar(2) DEFAULT NULL,
  `region_name` varchar(120) DEFAULT NULL,
  `is_registration_enabled` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `industry_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  `rejection_reason` longtext NOT NULL,
  `requested_by_id` bigint(20) DEFAULT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_opera_industry_id_8328e574_fk_catalog_r` (`industry_id`),
  KEY `tenancy_tenant_operation_created_at_79c76026` (`created_at`),
  KEY `tenancy_tenant_operation_tenant_id_93d74de8` (`tenant_id`),
  KEY `tenancy_tenant_opera_requested_by_id_97667d23_fk_accounts_` (`requested_by_id`),
  KEY `tenancy_tenant_opera_reviewed_by_id_2d87825d_fk_accounts_` (`reviewed_by_id`),
  CONSTRAINT `tenancy_tenant_opera_industry_id_8328e574_fk_catalog_r` FOREIGN KEY (`industry_id`) REFERENCES `catalog_reference_value` (`id`),
  CONSTRAINT `tenancy_tenant_opera_requested_by_id_97667d23_fk_accounts_` FOREIGN KEY (`requested_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_opera_reviewed_by_id_2d87825d_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_operation_tenant_id_93d74de8_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`),
  CONSTRAINT `chk_tenant_operation_dates` CHECK (`effective_from` is null or `effective_to` is null or `effective_from` <= `effective_to`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_operation`
--

LOCK TABLES `tenancy_tenant_operation` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_operation` DISABLE KEYS */;
INSERT INTO `tenancy_tenant_operation` VALUES (1,'2026-08-12 07:06:06.796736','2026-08-12 07:06:06.796764','IN','mumbai',1,1,NULL,NULL,1,1,'',NULL,NULL,NULL,'PENDING'),(2,'2026-08-12 07:06:35.133348','2026-08-12 07:06:35.133374','IN','mumbai',1,1,NULL,NULL,4,1,'',NULL,NULL,NULL,'PENDING'),(4,'2026-08-25 08:51:50.306105','2026-08-25 09:54:42.395162','US','New York',0,1,'2026-12-25','2030-01-25',1,3,'',NULL,NULL,NULL,'PENDING'),(5,'2026-08-25 09:04:13.591273','2026-08-25 09:54:42.638394','IN','Telangana',1,1,'2026-11-25','2029-05-25',3,3,'',NULL,NULL,NULL,'PENDING');
/*!40000 ALTER TABLE `tenancy_tenant_operation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_operation_log`
--

DROP TABLE IF EXISTS `tenancy_tenant_operation_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_operation_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `operation_type` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL,
  `remarks` longtext NOT NULL,
  `started_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `performed_by_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_opera_performed_by_id_c7dee713_fk_accounts_` (`performed_by_id`),
  KEY `tenancy_tenant_opera_tenant_id_d228528e_fk_tenancy_t` (`tenant_id`),
  CONSTRAINT `tenancy_tenant_opera_performed_by_id_c7dee713_fk_accounts_` FOREIGN KEY (`performed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_opera_tenant_id_d228528e_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_operation_log`
--

LOCK TABLES `tenancy_tenant_operation_log` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_operation_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_operation_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_report_template`
--

DROP TABLE IF EXISTS `tenancy_tenant_report_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_report_template` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `template_name` varchar(255) NOT NULL,
  `file` varchar(1000) NOT NULL,
  `version` varchar(50) NOT NULL,
  `status` varchar(20) NOT NULL,
  `approval_matrix` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`approval_matrix`)),
  `tenant_id` bigint(20) NOT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_repor_tenant_id_2c1707e9_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_report_template_created_at_7c925d32` (`created_at`),
  KEY `tenancy_tenant_repor_reviewed_by_id_4b36f125_fk_accounts_` (`reviewed_by_id`),
  CONSTRAINT `tenancy_tenant_repor_reviewed_by_id_4b36f125_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_repor_tenant_id_2c1707e9_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_report_template`
--

LOCK TABLES `tenancy_tenant_report_template` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_report_template` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_report_template` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_resume_template`
--

DROP TABLE IF EXISTS `tenancy_tenant_resume_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_resume_template` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `template_name` varchar(255) NOT NULL,
  `file` varchar(1000) NOT NULL,
  `version` varchar(50) NOT NULL,
  `status` varchar(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_resum_tenant_id_3c02d213_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_resume_template_created_at_daa71f8f` (`created_at`),
  CONSTRAINT `tenancy_tenant_resum_tenant_id_3c02d213_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_resume_template`
--

LOCK TABLES `tenancy_tenant_resume_template` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_resume_template` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_resume_template` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_role_assignment`
--

DROP TABLE IF EXISTS `tenancy_tenant_role_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_role_assignment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `assigned_at` datetime(6) NOT NULL,
  `granted_by_id` bigint(20) DEFAULT NULL,
  `membership_id` bigint(20) NOT NULL,
  `role_id` bigint(20) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_role__membership_id_4c79ab77_fk_tenancy_t` (`membership_id`),
  KEY `tenancy_tenant_role__role_id_01925314_fk_accounts_` (`role_id`),
  KEY `tenancy_tenant_role__user_id_65a5ad30_fk_accounts_` (`user_id`),
  KEY `tenancy_tenant_role__granted_by_id_caeb410b_fk_accounts_` (`granted_by_id`),
  CONSTRAINT `tenancy_tenant_role__granted_by_id_caeb410b_fk_accounts_` FOREIGN KEY (`granted_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_role__membership_id_4c79ab77_fk_tenancy_t` FOREIGN KEY (`membership_id`) REFERENCES `tenancy_tenant_membership` (`id`),
  CONSTRAINT `tenancy_tenant_role__role_id_01925314_fk_accounts_` FOREIGN KEY (`role_id`) REFERENCES `accounts_roles` (`id`),
  CONSTRAINT `tenancy_tenant_role__user_id_65a5ad30_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_role_assignment`
--

LOCK TABLES `tenancy_tenant_role_assignment` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_role_assignment` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_role_assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_scope`
--

DROP TABLE IF EXISTS `tenancy_tenant_scope`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_scope` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `scope_catalog_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  UNIQUE KEY `uniq_tenant_scope` (`tenant_id`,`scope_catalog_id`),
  KEY `tenancy_tenant_scope_scope_catalog_id_730e529e_fk_catalog_s` (`scope_catalog_id`),
  KEY `tenancy_tenant_scope_created_at_3bcc2b49` (`created_at`),
  CONSTRAINT `tenancy_tenant_scope_scope_catalog_id_730e529e_fk_catalog_s` FOREIGN KEY (`scope_catalog_id`) REFERENCES `catalog_scope_catalog` (`id`),
  CONSTRAINT `tenancy_tenant_scope_tenant_id_1864720a_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_scope`
--

LOCK TABLES `tenancy_tenant_scope` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_scope` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_scope` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_security_settings`
--

DROP TABLE IF EXISTS `tenancy_tenant_security_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_security_settings` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `mfa_policy` varchar(25) NOT NULL,
  `sso_status` varchar(15) NOT NULL,
  `identity_provider` varchar(100) NOT NULL,
  `session_policy` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`session_policy`)),
  `api_access_status` varchar(15) NOT NULL,
  `export_policy` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`export_policy`)),
  `updated_at` datetime(6) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `tenancy_tenant_secur_tenant_id_135c0c8a_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_security_settings`
--

LOCK TABLES `tenancy_tenant_security_settings` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_security_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_security_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_settings`
--

DROP TABLE IF EXISTS `tenancy_tenant_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_settings` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `default_language` varchar(10) NOT NULL,
  `date_format` varchar(20) NOT NULL,
  `number_format` varchar(20) NOT NULL,
  `measurement_system` varchar(10) NOT NULL,
  `working_calendar` varchar(100) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `tenancy_tenant_settings_tenant_id_d5dc84f4_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_settings`
--

LOCK TABLES `tenancy_tenant_settings` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_subscription`
--

DROP TABLE IF EXISTS `tenancy_tenant_subscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_subscription` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `plan` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `start_date` date NOT NULL,
  `renewal_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `seat_limit` int(10) unsigned NOT NULL CHECK (`seat_limit` >= 0),
  `project_limit` int(10) unsigned DEFAULT NULL CHECK (`project_limit` >= 0),
  `storage_limit_gb` int(10) unsigned DEFAULT NULL CHECK (`storage_limit_gb` >= 0),
  `used_seats` int(10) unsigned NOT NULL CHECK (`used_seats` >= 0),
  `used_projects` int(10) unsigned NOT NULL CHECK (`used_projects` >= 0),
  `used_storage_gb` decimal(12,2) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_subsc_tenant_id_17d04430_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_subscription_created_at_824f799e` (`created_at`),
  CONSTRAINT `tenancy_tenant_subsc_tenant_id_17d04430_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_subscription`
--

LOCK TABLES `tenancy_tenant_subscription` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_subscription` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_subscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_tax_registration`
--

DROP TABLE IF EXISTS `tenancy_tenant_tax_registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_tax_registration` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `tax_type` varchar(20) NOT NULL,
  `country_code` varchar(2) NOT NULL,
  `tax_number` text NOT NULL,
  `status` varchar(20) NOT NULL,
  `legal_entity_id` bigint(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_tax_r_legal_entity_id_9980cc38_fk_tenancy_t` (`legal_entity_id`),
  KEY `tenancy_tenant_tax_r_tenant_id_df63bc13_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_tax_registration_created_at_77609bf2` (`created_at`),
  CONSTRAINT `tenancy_tenant_tax_r_legal_entity_id_9980cc38_fk_tenancy_t` FOREIGN KEY (`legal_entity_id`) REFERENCES `tenancy_tenant_legal_entity` (`id`),
  CONSTRAINT `tenancy_tenant_tax_r_tenant_id_df63bc13_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_tax_registration`
--

LOCK TABLES `tenancy_tenant_tax_registration` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_tax_registration` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_tax_registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_terminology`
--

DROP TABLE IF EXISTS `tenancy_tenant_terminology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_terminology` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `canonical_code` varchar(100) NOT NULL,
  `display_label` varchar(100) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_tenant_terminology` (`tenant_id`,`canonical_code`),
  CONSTRAINT `tenancy_tenant_termi_tenant_id_8a2390c6_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_terminology`
--

LOCK TABLES `tenancy_tenant_terminology` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_terminology` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_terminology` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_verification`
--

DROP TABLE IF EXISTS `tenancy_tenant_verification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_verification` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `status` varchar(20) NOT NULL,
  `submitted_at` datetime(6) DEFAULT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `reason` longtext NOT NULL,
  `risk_classification` varchar(20) NOT NULL,
  `next_review_date` date DEFAULT NULL,
  `reviewed_by_id` bigint(20) DEFAULT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_verif_reviewed_by_id_d6814782_fk_accounts_` (`reviewed_by_id`),
  KEY `tenancy_tenant_verif_tenant_id_1ad523e3_fk_tenancy_t` (`tenant_id`),
  KEY `tenancy_tenant_verification_created_at_82aa7246` (`created_at`),
  CONSTRAINT `tenancy_tenant_verif_reviewed_by_id_d6814782_fk_accounts_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_verif_tenant_id_1ad523e3_fk_tenancy_t` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_verification`
--

LOCK TABLES `tenancy_tenant_verification` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_verification` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_verification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_workflow`
--

DROP TABLE IF EXISTS `tenancy_tenant_workflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_workflow` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `workflow_type` varchar(50) NOT NULL,
  `reference_table` varchar(50) NOT NULL,
  `reference_id` char(32) NOT NULL,
  `status` varchar(20) NOT NULL,
  `tenant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenancy_tenant_workflow_tenant_id_db1ac6d0_fk_tenancy_tenant_id` (`tenant_id`),
  KEY `tenancy_tenant_workflow_created_at_5a7a2535` (`created_at`),
  CONSTRAINT `tenancy_tenant_workflow_tenant_id_db1ac6d0_fk_tenancy_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenancy_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_workflow`
--

LOCK TABLES `tenancy_tenant_workflow` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_workflow` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_workflow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenancy_tenant_workflow_step`
--

DROP TABLE IF EXISTS `tenancy_tenant_workflow_step`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenancy_tenant_workflow_step` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `public_id` char(32) NOT NULL,
  `step_order` int(10) unsigned NOT NULL CHECK (`step_order` >= 0),
  `decision` varchar(30) NOT NULL,
  `comments` longtext NOT NULL,
  `actioned_at` datetime(6) DEFAULT NULL,
  `actioned_by_id` bigint(20) DEFAULT NULL,
  `assigned_role_id` bigint(20) NOT NULL,
  `workflow_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_id` (`public_id`),
  KEY `tenancy_tenant_workf_actioned_by_id_3288344b_fk_accounts_` (`actioned_by_id`),
  KEY `tenancy_tenant_workf_assigned_role_id_fc8956aa_fk_accounts_` (`assigned_role_id`),
  KEY `tenancy_tenant_workf_workflow_id_7c66467d_fk_tenancy_t` (`workflow_id`),
  CONSTRAINT `tenancy_tenant_workf_actioned_by_id_3288344b_fk_accounts_` FOREIGN KEY (`actioned_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tenancy_tenant_workf_assigned_role_id_fc8956aa_fk_accounts_` FOREIGN KEY (`assigned_role_id`) REFERENCES `accounts_roles` (`id`),
  CONSTRAINT `tenancy_tenant_workf_workflow_id_7c66467d_fk_tenancy_t` FOREIGN KEY (`workflow_id`) REFERENCES `tenancy_tenant_workflow` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenancy_tenant_workflow_step`
--

LOCK TABLES `tenancy_tenant_workflow_step` WRITE;
/*!40000 ALTER TABLE `tenancy_tenant_workflow_step` DISABLE KEYS */;
/*!40000 ALTER TABLE `tenancy_tenant_workflow_step` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_blacklistedtoken`
--

LOCK TABLES `token_blacklist_blacklistedtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `jti` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outs_user_id_83bc629a_fk_auth_user` (`user_id`),
  CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_outstandingtoken`
--

LOCK TABLES `token_blacklist_outstandingtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-26 10:58:44

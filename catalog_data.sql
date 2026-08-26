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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-26 11:37:49

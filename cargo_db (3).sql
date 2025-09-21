-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 21, 2025 at 07:54 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cargo_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `cargo_bookings`
--

CREATE TABLE `cargo_bookings` (
  `id` int(11) NOT NULL,
  `tracking_id` varchar(20) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `sender_name` varchar(100) NOT NULL,
  `sender_address` text NOT NULL,
  `sender_phone` varchar(20) DEFAULT NULL,
  `recipient_name` varchar(100) NOT NULL,
  `recipient_address` text NOT NULL,
  `recipient_phone` varchar(20) DEFAULT NULL,
  `cargo_description` text DEFAULT NULL,
  `weight` decimal(10,2) DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `status` enum('pending','confirmed','in_transit','delivered','cancelled') DEFAULT 'pending',
  `origin_city` varchar(100) DEFAULT NULL,
  `destination_city` varchar(100) DEFAULT NULL,
  `booking_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `expected_delivery_date` date DEFAULT NULL,
  `actual_delivery_date` date DEFAULT NULL,
  `assigned_employee_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `sender_company` varchar(100) DEFAULT NULL,
  `sender_email` varchar(100) DEFAULT NULL,
  `recipient_company` varchar(100) DEFAULT NULL,
  `recipient_email` varchar(100) DEFAULT NULL,
  `alternative_contact_name` varchar(100) DEFAULT NULL,
  `alternative_contact_phone` varchar(20) DEFAULT NULL,
  `cargo_type` varchar(50) DEFAULT NULL,
  `number_of_pieces` int(11) DEFAULT 1,
  `dimensions` varchar(50) DEFAULT NULL,
  `package_value` decimal(10,2) DEFAULT NULL,
  `special_instructions` text DEFAULT NULL,
  `service_type` enum('economy','standard','express','overnight') DEFAULT 'standard',
  `preferred_delivery_date` date DEFAULT NULL,
  `delivery_instructions` text DEFAULT NULL,
  `insurance_required` tinyint(1) DEFAULT 0,
  `insurance_coverage` decimal(10,2) DEFAULT NULL,
  `insurance_premium` decimal(10,2) DEFAULT NULL,
  `pickup_required` tinyint(1) DEFAULT 0,
  `pickup_date` date DEFAULT NULL,
  `pickup_time` varchar(20) DEFAULT NULL,
  `cod_required` tinyint(1) DEFAULT 0,
  `cod_amount` decimal(10,2) DEFAULT NULL,
  `signature_required` tinyint(1) DEFAULT 0,
  `payment_method` enum('cash','card','upi','bank_transfer','corporate') DEFAULT 'cash',
  `reference_number` varchar(50) DEFAULT NULL,
  `notifications_email` tinyint(1) DEFAULT 1,
  `notifications_sms` tinyint(1) DEFAULT 1,
  `base_cost` decimal(10,2) DEFAULT NULL,
  `service_charges` decimal(10,2) DEFAULT NULL,
  `insurance_cost` decimal(10,2) DEFAULT NULL,
  `pickup_charges` decimal(10,2) DEFAULT NULL,
  `taxes` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cargo_bookings`
--

INSERT INTO `cargo_bookings` (`id`, `tracking_id`, `customer_id`, `sender_name`, `sender_address`, `sender_phone`, `recipient_name`, `recipient_address`, `recipient_phone`, `cargo_description`, `weight`, `total_amount`, `status`, `origin_city`, `destination_city`, `booking_date`, `expected_delivery_date`, `actual_delivery_date`, `assigned_employee_id`, `created_at`, `updated_at`, `sender_company`, `sender_email`, `recipient_company`, `recipient_email`, `alternative_contact_name`, `alternative_contact_phone`, `cargo_type`, `number_of_pieces`, `dimensions`, `package_value`, `special_instructions`, `service_type`, `preferred_delivery_date`, `delivery_instructions`, `insurance_required`, `insurance_coverage`, `insurance_premium`, `pickup_required`, `pickup_date`, `pickup_time`, `cod_required`, `cod_amount`, `signature_required`, `payment_method`, `reference_number`, `notifications_email`, `notifications_sms`, `base_cost`, `service_charges`, `insurance_cost`, `pickup_charges`, `taxes`) VALUES
(1, 'C8FA6767', 2, 'Ebin Sam', 'Golden villa pazhayakada thirupuram P.O', '09745396058', 'Ebi Sae', 'Gold villa pazhayakada thirupram P.O', '09745396053', 'retfhgsertfhgrfdg', 234.00, 1232.00, '', NULL, NULL, '2025-09-21 16:23:35', '2025-09-26', NULL, NULL, '2025-09-21 16:23:35', '2025-09-21 17:51:06', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1232.00, NULL, 'standard', NULL, NULL, 0, NULL, NULL, 0, NULL, NULL, 0, NULL, 0, 'cash', NULL, 1, 1, NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `address` text DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`id`, `user_id`, `address`, `phone`, `created_at`, `updated_at`) VALUES
(1, 3, '456 Oak Avenue', '+0987654321', '2025-09-21 10:10:53', '2025-09-21 10:10:53'),
(2, 4, NULL, NULL, '2025-09-21 10:28:22', '2025-09-21 10:28:22');

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `employee_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `employee_code` varchar(20) NOT NULL,
  `department` enum('logistics','warehouse','customer_service','management','driver') NOT NULL,
  `position` varchar(50) DEFAULT NULL,
  `hire_date` date DEFAULT curdate(),
  `manager_id` int(11) DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `employment_type` enum('Full-time','Contract','Outsourced') DEFAULT 'Full-time',
  `location` varchar(100) DEFAULT NULL,
  `salary` decimal(10,2) DEFAULT 0.00,
  `photo` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employees`
--

INSERT INTO `employees` (`employee_id`, `user_id`, `employee_code`, `department`, `position`, `hire_date`, `manager_id`, `phone_number`, `address`, `employment_type`, `location`, `salary`, `photo`, `created_at`, `updated_at`) VALUES
(1, 2, 'EMP001', 'logistics', 'Logistics Coordinator', '2025-09-21', NULL, '+1234567890', '123 Main St', 'Full-time', 'Warehouse A', 0.00, NULL, '2025-09-21 10:10:53', '2025-09-21 10:10:53');

-- --------------------------------------------------------

--
-- Table structure for table `invoices`
--

CREATE TABLE `invoices` (
  `id` int(11) NOT NULL,
  `booking_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` enum('paid','pending','overdue','cancelled') DEFAULT 'pending',
  `issued_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `paid_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `type` enum('email','sms','system') DEFAULT 'system',
  `status` enum('sent','pending','failed') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `generated_by` int(11) DEFAULT NULL,
  `report_type` varchar(50) DEFAULT NULL,
  `parameters` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`parameters`)),
  `file_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `support_tickets`
--

CREATE TABLE `support_tickets` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `status` enum('open','in_progress','closed') DEFAULT 'open',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `system_logs`
--

CREATE TABLE `system_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(255) DEFAULT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`details`)),
  `log_time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tracking_updates`
--

CREATE TABLE `tracking_updates` (
  `id` int(11) NOT NULL,
  `booking_id` int(11) NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `status` enum('pending','confirmed','dispatched','in_transit','arrived','delivered','cancelled') NOT NULL,
  `notes` text DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tracking_updates`
--

INSERT INTO `tracking_updates` (`id`, `booking_id`, `location`, `status`, `notes`, `updated_at`) VALUES
(1, 1, 'Shipment Booked', 'pending', 'Shipment created by customer', '2025-09-21 16:23:35'),
(2, 1, '', 'confirmed', '', '2025-09-21 17:41:46'),
(3, 1, 'kollam', 'dispatched', 'hi hi', '2025-09-21 17:51:06');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `fullname` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('admin','customer','employee') NOT NULL,
  `status` enum('active','inactive','suspended') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `must_change_password` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `fullname`, `username`, `email`, `password_hash`, `role`, `status`, `created_at`, `updated_at`, `must_change_password`) VALUES
(1, 'Admin User', 'admin', 'admin@cargo.com', 'scrypt:32768:8:1$nF5ofFYYr5gnYLs6$97c2bd06b02cc1b63ad4c5c64e06d33ca497e7fe08276b39acebfe5fd8b324cfc01d1ce56fb90a4d1a3613e610b884f63a8f4b8272086d49b650813b559e6295', 'admin', 'active', '2025-09-21 10:10:53', '2025-09-21 10:10:53', 1),
(2, 'Jane Employee', 'jane', 'jane@cargo.com', 'scrypt:32768:8:1$JxlqPJY5SJqM6kkY$e547bbb2ffb86827359240f534652b7fd95b5833569ddcf0558ba689109a484b21dec79ce6f1b6df694f590de28bf0ba6372bee56b50baa265d923e2987a3783', 'employee', 'active', '2025-09-21 10:10:53', '2025-09-21 10:10:53', 1),
(3, 'John Customer', 'john', 'john@cargo.com', 'scrypt:32768:8:1$74NyBRTX6vAAwWjK$b8fb207cb18d7444726b0bfa740894cf88366b50b90bb6d39a8a446db172196e16a15b7d023352be4f4790418136978a064407ac80b6931c4f92be5e2ff8bd62', 'customer', 'active', '2025-09-21 10:10:53', '2025-09-21 10:10:53', 1),
(4, 'ebin', 'ebin', 'ebin@gmail.com', 'scrypt:32768:8:1$oVJ9OywaS55nvXk1$fefac4e72da9fb90ac286488e13f518a224e5bc69c3ec47cd9f7374f2a3052dc59fc654ae4eb2957d26b293990ffc1c96d4af7eeaee956f0859a15f691cb9ce8', 'customer', 'active', '2025-09-21 10:28:22', '2025-09-21 10:28:22', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cargo_bookings`
--
ALTER TABLE `cargo_bookings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_tracking_id` (`tracking_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `assigned_employee_id` (`assigned_employee_id`),
  ADD KEY `idx_cargo_status` (`status`),
  ADD KEY `idx_cargo_date` (`booking_date`),
  ADD KEY `idx_cargo_type` (`cargo_type`),
  ADD KEY `idx_service_type` (`service_type`),
  ADD KEY `idx_payment_method` (`payment_method`),
  ADD KEY `idx_pickup_date` (`pickup_date`),
  ADD KEY `idx_preferred_delivery` (`preferred_delivery_date`);

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`employee_id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD UNIQUE KEY `employee_code` (`employee_code`),
  ADD KEY `fk_employee_manager` (`manager_id`);

--
-- Indexes for table `invoices`
--
ALTER TABLE `invoices`
  ADD PRIMARY KEY (`id`),
  ADD KEY `booking_id` (`booking_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `generated_by` (`generated_by`);

--
-- Indexes for table `support_tickets`
--
ALTER TABLE `support_tickets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `tracking_updates`
--
ALTER TABLE `tracking_updates`
  ADD PRIMARY KEY (`id`),
  ADD KEY `booking_id` (`booking_id`),
  ADD KEY `idx_tracking_status` (`status`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_users_role` (`role`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cargo_bookings`
--
ALTER TABLE `cargo_bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `employees`
--
ALTER TABLE `employees`
  MODIFY `employee_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `invoices`
--
ALTER TABLE `invoices`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `support_tickets`
--
ALTER TABLE `support_tickets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `system_logs`
--
ALTER TABLE `system_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tracking_updates`
--
ALTER TABLE `tracking_updates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cargo_bookings`
--
ALTER TABLE `cargo_bookings`
  ADD CONSTRAINT `cargo_bookings_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cargo_bookings_ibfk_2` FOREIGN KEY (`assigned_employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL;

--
-- Constraints for table `customers`
--
ALTER TABLE `customers`
  ADD CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `employees`
--
ALTER TABLE `employees`
  ADD CONSTRAINT `fk_employee_manager` FOREIGN KEY (`manager_id`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_employee_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `invoices`
--
ALTER TABLE `invoices`
  ADD CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `cargo_bookings` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`generated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `support_tickets`
--
ALTER TABLE `support_tickets`
  ADD CONSTRAINT `support_tickets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD CONSTRAINT `system_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `tracking_updates`
--
ALTER TABLE `tracking_updates`
  ADD CONSTRAINT `tracking_updates_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `cargo_bookings` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

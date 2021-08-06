SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `capstone`
--

-- --------------------------------------------------------

--
-- Table structure for table `Announcements`
--

CREATE TABLE `Announcements` (
  `a_id` int(11) NOT NULL,
  `title` longtext NOT NULL,
  `description` longtext NOT NULL,
  `dated` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Evaluations`
--

CREATE TABLE `Evaluations` (
  `evaluation_no` int(11) NOT NULL,
  `max_marks` int(11) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Group_Mentors`
--

CREATE TABLE `Group_Mentors` (
  `group_id` int(11) NOT NULL,
  `mentor1_id` int(11) NOT NULL,
  `mentor2_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Heads`
--

CREATE TABLE `Heads` (
  `mentor_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `Heads`
--
-- --------------------------------------------------------

--
-- Table structure for table `Mentors`
--

CREATE TABLE `Mentors` (
  `mentor_id` int(11) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `group_limit` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '2',
  `reset_link` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Panelists`
--

CREATE TABLE `Panelists` (
  `panel_no` int(11) NOT NULL,
  `panel_id` int(11) NOT NULL,
  `mentor_id` int(11) NOT NULL,
  `head` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Panel_Group`
--

CREATE TABLE `Panel_Group` (
  `panel_no` int(11) NOT NULL,
  `panel_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `filled` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Panel_Marks`
--

CREATE TABLE `Panel_Marks` (
  `roll_no` int(11) NOT NULL,
  `panel_no` int(11) NOT NULL,
  `parameter1_marks` int(11) DEFAULT NULL,
  `parameter2_marks` int(11) DEFAULT NULL,
  `parameter3_marks` int(11) DEFAULT NULL,
  `parameter4_marks` int(11) DEFAULT NULL,
  `parameter5_marks` int(11) DEFAULT NULL,
  `parameter6_marks` int(11) DEFAULT NULL,
  `parameter7_marks` int(11) DEFAULT NULL,
  `parameter8_marks` int(11) DEFAULT NULL,
  `parameter9_marks` int(11) DEFAULT NULL,
  `parameter10_marks` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Table structure for table `Panel_Parameter`
--

CREATE TABLE `Panel_Parameter` (
  `panel_no` int(11) NOT NULL,
  `parameter_no` int(11) NOT NULL,
  `name` longtext COLLATE utf8mb4_unicode_ci,
  `max_marks` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Requests`
--

CREATE TABLE `Requests` (
  `group_id` int(11) NOT NULL,
  `leader_roll_no` int(11) NOT NULL,
  `title` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `student2_roll_no` int(11) NOT NULL,
  `student3_roll_no` int(11) DEFAULT NULL,
  `student4_roll_no` int(11) DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `leader_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `student2_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `student3_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student4_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mentor_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Students`
--

CREATE TABLE `Students` (
  `group_id` int(11) NOT NULL,
  `roll_no` int(11) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `evaluation1_marks` int(11) DEFAULT NULL,
  `evaluation2_marks` int(11) DEFAULT NULL,
  `evaluation3_marks` int(11) DEFAULT NULL,
  `evaluation4_marks` int(11) DEFAULT NULL,
  `evaluation5_marks` int(11) DEFAULT NULL,
  `evaluation6_marks` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Teams`
--

CREATE TABLE `Teams` (
  `group_id` int(11) NOT NULL,
  `leader_roll_no` int(11) NOT NULL,
  `title` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `student2_roll_no` int(11) NOT NULL,
  `student3_roll_no` int(11) DEFAULT NULL,
  `student4_roll_no` int(11) DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `objective` longtext COLLATE utf8mb4_unicode_ci,
  `password` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


--
-- Indexes for table `Announcements`
--
ALTER TABLE `Announcements`
  ADD PRIMARY KEY (`a_id`);

--
-- Indexes for table `Evaluations`
--
ALTER TABLE `Evaluations`
  ADD PRIMARY KEY (`evaluation_no`);

--
-- Indexes for table `Group_Mentors`
--
ALTER TABLE `Group_Mentors`
  ADD PRIMARY KEY (`group_id`),
  ADD KEY `mentor1_id` (`mentor1_id`),
  ADD KEY `mentor2_id` (`mentor2_id`);

--
-- Indexes for table `Heads`
--
ALTER TABLE `Heads`
  ADD PRIMARY KEY (`mentor_id`);

--
-- Indexes for table `Mentors`
--
ALTER TABLE `Mentors`
  ADD PRIMARY KEY (`mentor_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `Panelists`
--
ALTER TABLE `Panelists`
  ADD PRIMARY KEY (`panel_no`,`panel_id`,`mentor_id`),
  ADD KEY `fk5` (`mentor_id`);

--
-- Indexes for table `Panel_Group`
--
ALTER TABLE `Panel_Group`
  ADD PRIMARY KEY (`panel_no`,`panel_id`,`group_id`),
  ADD KEY `fk6` (`group_id`);

--
-- Indexes for table `Panel_Marks`
--
ALTER TABLE `Panel_Marks`
  ADD PRIMARY KEY (`roll_no`,`panel_no`);

--
-- Indexes for table `Panel_Parameter`
--
ALTER TABLE `Panel_Parameter`
  ADD PRIMARY KEY (`panel_no`,`parameter_no`);

--
-- Indexes for table `Requests`
--
ALTER TABLE `Requests`
  ADD PRIMARY KEY (`group_id`),
  ADD KEY `mentor_id` (`mentor_id`);

--
-- Indexes for table `Students`
--
ALTER TABLE `Students`
  ADD PRIMARY KEY (`group_id`,`roll_no`);

--
-- Indexes for table `Teams`
--
ALTER TABLE `Teams`
  ADD PRIMARY KEY (`group_id`);

--
-- AUTO_INCREMENT for table `Announcements`
--
ALTER TABLE `Announcements`
  MODIFY `a_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT for table `Evaluations`
--
ALTER TABLE `Evaluations`
  MODIFY `evaluation_no` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
--
-- AUTO_INCREMENT for table `Mentors`
--
ALTER TABLE `Mentors`
  MODIFY `mentor_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=59;
--
-- AUTO_INCREMENT for table `Requests`
--
ALTER TABLE `Requests`
  MODIFY `group_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
--
-- AUTO_INCREMENT for table `Teams`
--
ALTER TABLE `Teams`
  MODIFY `group_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for table `Group_Mentors`
--
ALTER TABLE `Group_Mentors`
  ADD CONSTRAINT `fk` FOREIGN KEY (`group_id`) REFERENCES `Teams` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk2` FOREIGN KEY (`mentor1_id`) REFERENCES `Mentors` (`mentor_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk3` FOREIGN KEY (`mentor2_id`) REFERENCES `Mentors` (`mentor_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `Heads`
--
ALTER TABLE `Heads`
  ADD CONSTRAINT `Heads_ibfk_1` FOREIGN KEY (`mentor_id`) REFERENCES `Mentors` (`mentor_id`);

--
-- Constraints for table `Panelists`
--
ALTER TABLE `Panelists`
  ADD CONSTRAINT `fk5` FOREIGN KEY (`mentor_id`) REFERENCES `Mentors` (`mentor_id`) ON DELETE CASCADE;

--
-- Constraints for table `Panel_Group`
--
ALTER TABLE `Panel_Group`
  ADD CONSTRAINT `fk6` FOREIGN KEY (`group_id`) REFERENCES `Teams` (`group_id`) ON DELETE CASCADE;

--
-- Constraints for table `Requests`
--
ALTER TABLE `Requests`
  ADD CONSTRAINT `Requests_ibfk_1` FOREIGN KEY (`mentor_id`) REFERENCES `Mentors` (`mentor_id`);

--
-- Constraints for table `Students`
--
ALTER TABLE `Students`
  ADD CONSTRAINT `fk4` FOREIGN KEY (`group_id`) REFERENCES `Teams` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

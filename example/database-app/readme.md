Learning Platform System (Laravel Eloquent Relationships)

This document describes a sample system designed to utilize all major Laravel Eloquent relationship types in a practical and scalable way.

🧩 Overview

A simplified learning platform where:

Users can be students or instructors
Instructors create courses
Courses contain lessons
Students enroll in courses
Users can leave reviews on courses or lessons
🏗️ Entities
User
Profile
Course
Lesson
Enrollment (pivot)
Review
Category
🔗 Relationships
1. User
class User extends Model
{
    // One-to-One
    public function profile()
    {
        return $this->hasOne(Profile::class);
    }

    // One-to-Many (Instructor → Courses)
    public function courses()
    {
        return $this->hasMany(Course::class, 'instructor_id');
    }

    // Many-to-Many (Student → Enrollments)
    public function enrolledCourses()
    {
        return $this->belongsToMany(Course::class)
            ->withPivot(['progress', 'completed_at'])
            ->withTimestamps();
    }

    // Has Many Through (Instructor → Lessons)
    public function lessons()
    {
        return $this->hasManyThrough(
            Lesson::class,
            Course::class,
            'instructor_id',
            'course_id',
            'id',
            'id'
        );
    }
}
2. Profile
class Profile extends Model
{
    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
3. Course
class Course extends Model
{
    // Belongs to Instructor
    public function instructor()
    {
        return $this->belongsTo(User::class, 'instructor_id');
    }

    // One-to-Many
    public function lessons()
    {
        return $this->hasMany(Lesson::class);
    }

    // Many-to-Many
    public function students()
    {
        return $this->belongsToMany(User::class)
            ->withPivot(['progress', 'completed_at'])
            ->withTimestamps();
    }

    // Polymorphic
    public function reviews()
    {
        return $this->morphMany(Review::class, 'reviewable');
    }

    // Category relation
    public function category()
    {
        return $this->belongsTo(Category::class);
    }
}
4. Lesson
class Lesson extends Model
{
    public function course()
    {
        return $this->belongsTo(Course::class);
    }

    public function reviews()
    {
        return $this->morphMany(Review::class, 'reviewable');
    }
}
5. Enrollment (Pivot Table: course_user)
// No dedicated model required unless needed
// Table: course_user

Schema::create('course_user', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id');
    $table->foreignId('course_id');
    $table->integer('progress')->default(0);
    $table->timestamp('completed_at')->nullable();
    $table->timestamps();
});
6. Review (Polymorphic)
class Review extends Model
{
    public function reviewable()
    {
        return $this->morphTo();
    }
}
7. Category
class Category extends Model
{
    public function courses()
    {
        return $this->hasMany(Course::class);
    }
}
🗄️ Database Structure
users
id
name
email
profiles
id
user_id
bio
courses
id
title
instructor_id
category_id
lessons
id
course_id
title
course_user (pivot)
user_id
course_id
progress
completed_at
reviews
id
reviewable_id
reviewable_type
content
categories
id
name
🧠 Relationship Summary
Type	Example
hasOne	User → Profile
belongsTo	Course → User (Instructor)
hasMany	Course → Lessons
belongsToMany	User ↔ Courses (Enrollment)
hasManyThrough	User → Lessons via Courses
morphMany	Course/Lesson → Reviews
morphTo	Review → Course/Lesson
🚀 Notes
Use with() for eager loading to avoid N+1 queries
Use pivot data for tracking progress and completion
Add indexes on foreign keys for performance
Consider policies for authorization (Instructor vs Student)
💡 Possible Extensions
Quizzes (hasMany from Lesson)
Certificates (hasOne from Enrollment)
Tags (belongsToMany)
Payments (Stripe integration)

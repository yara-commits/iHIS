from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.rehabilitation import (TherapyAssessment, TherapyPlan,
                                   TherapySession, ExerciseLibrary,
                                   RehabProgress, FunctionalOutcome)
from models.patient import Patient
from datetime import datetime

rehabilitation = Blueprint('rehabilitation', __name__)


def rehab_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['therapist', 'admin', 'superadmin']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@rehabilitation.route('/')
@login_required
@rehab_required
def index():
    active_plans = TherapyPlan.query.filter_by(status='active').count()
    todays_sessions = TherapySession.query.filter(
        db.func.date(TherapySession.session_date) == datetime.utcnow().date()
    ).count()
    total_patients = TherapyAssessment.query.distinct(
        TherapyAssessment.patient_id
    ).count()
    recent_assessments = TherapyAssessment.query.order_by(
        TherapyAssessment.created_at.desc()
    ).limit(10).all()
    return render_template('rehabilitation/index.html',
                           active_plans=active_plans,
                           todays_sessions=todays_sessions,
                           total_patients=total_patients,
                           recent_assessments=recent_assessments)


@rehabilitation.route('/assess/<int:patient_id>/new', methods=['GET', 'POST'])
@login_required
@rehab_required
def new_assessment(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        assessment = TherapyAssessment(
            patient_id=patient_id,
            therapist_id=current_user.id,
            pain_score=request.form.get('pain_score'),
            mobility_score=request.form.get('mobility_score'),
            strength_score=request.form.get('strength_score'),
            balance_score=request.form.get('balance_score'),
            functional_score=request.form.get('functional_score'),
            functional_assessment=request.form.get('functional_assessment'),
            mobility_assessment=request.form.get('mobility_assessment'),
            muscle_strength=request.form.get('muscle_strength'),
            range_of_motion=request.form.get('range_of_motion'),
            posture_evaluation=request.form.get('posture_evaluation'),
            gait_analysis=request.form.get('gait_analysis'),
            notes=request.form.get('notes')
        )
        db.session.add(assessment)
        db.session.commit()
        flash('Assessment completed!', 'success')
        return redirect(url_for('rehabilitation.new_plan',
                                assessment_id=assessment.id))

    return render_template('rehabilitation/assessment.html', patient=patient)


@rehabilitation.route('/plan/<int:assessment_id>/new', methods=['GET', 'POST'])
@login_required
@rehab_required
def new_plan(assessment_id):
    assessment = TherapyAssessment.query.get_or_404(assessment_id)
    patient = Patient.query.get_or_404(assessment.patient_id)
    if request.method == 'POST':
        plan = TherapyPlan(
            assessment_id=assessment_id,
            patient_id=assessment.patient_id,
            therapist_id=current_user.id,
            goals=request.form.get('goals'),
            modalities=request.form.get('modalities'),
            frequency=request.form.get('frequency'),
            duration_weeks=request.form.get('duration_weeks'),
            start_date=datetime.strptime(
                request.form.get('start_date'), '%Y-%m-%d'
            ).date(),
            status='active',
            notes=request.form.get('notes')
        )
        db.session.add(plan)
        db.session.commit()
        flash('Therapy plan created!', 'success')
        return redirect(url_for('rehabilitation.view_plan', id=plan.id))

    return render_template('rehabilitation/new_plan.html',
                           assessment=assessment,
                           patient=patient)


@rehabilitation.route('/plan/<int:id>')
@login_required
@rehab_required
def view_plan(id):
    plan = TherapyPlan.query.get_or_404(id)
    sessions = TherapySession.query.filter_by(
        plan_id=id
    ).order_by(TherapySession.session_date.desc()).all()
    progress = RehabProgress.query.filter_by(plan_id=id).all()
    outcomes = FunctionalOutcome.query.filter_by(plan_id=id).all()
    exercises = ExerciseLibrary.query.filter_by(is_active=True).all()
    return render_template('rehabilitation/plan.html',
                           plan=plan,
                           sessions=sessions,
                           progress=progress,
                           outcomes=outcomes,
                           exercises=exercises)


@rehabilitation.route('/session/<int:plan_id>/add', methods=['GET', 'POST'])
@login_required
@rehab_required
def add_session(plan_id):
    plan = TherapyPlan.query.get_or_404(plan_id)
    if request.method == 'POST':
        session = TherapySession(
            plan_id=plan_id,
            therapist_id=current_user.id,
            duration_minutes=request.form.get('duration_minutes', 60),
            pain_before=request.form.get('pain_before'),
            pain_after=request.form.get('pain_after'),
            exercises_done=request.form.get('exercises_done'),
            techniques_used=request.form.get('techniques_used'),
            patient_response=request.form.get('patient_response'),
            home_program=request.form.get('home_program'),
            notes=request.form.get('notes')
        )
        db.session.add(session)

        # Track progress
        if request.form.get('progress_value'):
            progress = RehabProgress(
                plan_id=plan_id,
                measurement_type=request.form.get('measurement_type'),
                value=float(request.form.get('progress_value')),
                unit=request.form.get('progress_unit'),
                notes=request.form.get('progress_notes')
            )
            db.session.add(progress)

        db.session.commit()
        flash('Session recorded!', 'success')
        return redirect(url_for('rehabilitation.view_plan', id=plan_id))

    exercises = ExerciseLibrary.query.filter_by(is_active=True).all()
    return render_template('rehabilitation/add_session.html',
                           plan=plan,
                           exercises=exercises)


@rehabilitation.route('/exercises')
@login_required
@rehab_required
def exercises():
    category = request.args.get('category', 'all')
    if category == 'all':
        exercises = ExerciseLibrary.query.filter_by(
            is_active=True
        ).all()
    else:
        exercises = ExerciseLibrary.query.filter_by(
            is_active=True,
            category=category
        ).all()
    return render_template('rehabilitation/exercises.html',
                           exercises=exercises,
                           category=category)


@rehabilitation.route('/exercises/add', methods=['GET', 'POST'])
@login_required
@rehab_required
def add_exercise():
    if request.method == 'POST':
        exercise = ExerciseLibrary(
            name=request.form.get('name'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            instructions=request.form.get('instructions'),
            sets=request.form.get('sets'),
            reps=request.form.get('reps'),
            duration_seconds=request.form.get('duration_seconds'),
            image_url=request.form.get('image_url'),
            video_url=request.form.get('video_url'),
            difficulty=request.form.get('difficulty')
        )
        db.session.add(exercise)
        db.session.commit()
        flash('Exercise added to library!', 'success')
        return redirect(url_for('rehabilitation.exercises'))

    return render_template('rehabilitation/add_exercise.html')
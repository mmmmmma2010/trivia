import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import func
from flask_cors import CORS
import random
import sys, os
from models import setup_db, Question, Category ,db

QUESTIONS_PER_PAGE = 10
random_num = 0


def paginate_Questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    Questions = [question.format() for question in selection]
    current_Questions = Questions[start:end]

    return current_Questions

def test_previous(isprevious,previous_question,iscategory=None):
    if iscategory:
        random_num =int(random.choice(db.session.query(Question.id).filter_by(category = iscategory).all())[0]) 
        while isprevious:
            for q in previous_question:
                if random_num == q:
                    isprevious=True
                    random_num = random.randrange(db.session.query(Question.id).filter_by(category= iscategory).all())
                    break
                else:
                    isprevious=False

    else:
        random_num = random.randint((db.session.query(func.min(Question.id).label('min_num')).one()).min_num, (db.session.query(func.max(Question.id).label('max_num')).one()).max_num)
        while isprevious:
            for q in previous_question:
                if random_num == q:
                    isprevious=True
                    random_num = random.randint((db.session.query(func.min(Question.id).label('min_num')).one()).min_num, (db.session.query(func.max(Question.id).label('max_num')).one()).max_num)
                    break
                else:
                    isprevious=False
    return random_num


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def afterrequest(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    @app.route('/categories')
    def get_categories():
        selection = Category.query.all()
        cats = [cat.format() for cat in selection]
        if len(cats) <= 0:
            abort(405)

        return jsonify({
            'sucsess': True,
            'categories':  cats

        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        selection1 = Category.query.all()
        cats = [cat.format() for cat in selection1]
        current_category= cats[0]

        if len(selection) <= 0:
            abort(404)
        questions = paginate_Questions(request, selection)
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(Question.query.all()),
            'categories': cats,
            'current_category':current_category
        })

    @app.route('/questions/<int:question_ID>', methods=['DELETE'])
    def delete_questions(question_ID):
        question = Question.query.filter_by(id = question_ID).first()
        try:
            if question is None:
                abort(404)
            question.delete()

            selection = Question.query.all()
            questions = paginate_Questions(request, selection)
            return jsonify({
                'success': True,
                'deleted': question_ID,
                'questions': questions
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_questions():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        search = body.get('searchTerm', None)
        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(search)))
                questions = paginate_Questions(request, selection)
                return jsonify({
                    'success': True,
                    'questions': questions,
                    'total_questions': len(Question.query.all())
                })
            else:
                question1 = Question(question=new_question, answer=new_answer,
                                    difficulty=new_difficulty,category=new_category)
                question1.insert()
                selection = Question.query.order_by(Question.id).all()
                questions = paginate_Questions(request, selection)
                return jsonify({
                    'success': True,
                    'questions': questions,
                    'total_questions': len(Question.query.all())
                })
        except Exception as ex :
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            return(jsonify({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
    }))
    @app.route('/categories/<category_id>/questions')
    def get_questions_with_category(category_id):
        selection = Question.query.order_by(Question.id).filter(
            Question.category == category_id).all()

        if len(selection) <= 0:
            abort(404)

        questions = paginate_Questions(request, selection)
        return jsonify({
            'success': True,
            'questions': questions,
            'current_category': category_id,
            'total_questions': len(selection)
            
        })

    @app.route('/quizzes', methods=['POST'])
    def random_question_game():
        try:
            body = request.get_json()  
            Bcategory = body.get('quiz_category', None)
            previous_question = body.get('previous_questions', None)
            isprevious=True
            if Bcategory:
                if previous_question:
                    question_id=test_previous(isprevious,previous_question,Bcategory)                                                      
                    question = Question.query.filter(
                        Question.id == question_id ).first()
                    return jsonify({
                        'success': True,
                        'question': question.format()
                    })
                else:
                    question_id=test_previous(False,previous_question,Bcategory)
                    question = db.session.query(Question).filter_by(
                        id = question_id).first()
                    return jsonify({
                        'success': True,
                        'question': question.format()
                    })
            else:
                if previous_question:
                    question_id=test_previous(isprevious,previous_question,Bcategory)

                    question = Question.query.filter(
                        Question.id == question_id).first()
                    return jsonify({
                        'success': True,
                        'question': question.format()
                    })
                else:
                    question_id=test_previous(False,previous_question,Bcategory)
                    question = Question.query.filter(
                        Question.id == question_id).first()
                    return jsonify({
                        'success': True,
                        'question': question.format()
                    })
        except Exception as ex :
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            return(jsonify({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace}))


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
    return app

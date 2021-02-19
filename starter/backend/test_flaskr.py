import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from collections import abc
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('Mohamed Ali','','127.0.0.1:5432', self.database_name)
        setup_db(self.app, self.database_path)



        self.New_question={
        'question':'What boxer original name is Cassius Clay?',
        'answer':'Mohamed Ali',
        'difficulty':1,
        'category':4 }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
     
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_Categories(self):
        res=self.client().get('/categories')
        data =json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['sucsess'],True)


    def test_get_questions(self):
        res = self.client().get('/questions')
        data= json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertGreater(data['total_questions'],0)


    def test_delete_questions(self):
        id=9
        res = self.client().delete('/questions/'+str(id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],id)

    def test_create_question(self):

        res= self.client().post('/questions',json=self.New_question)
        data= json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertGreater(data['total_questions'],0)

    def test_search(self):
        res = self.client().post('/questions',json={'search':'what'})
        data= json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)


    def test_get_questions_with_category(self):
        category_id="1"
        res = self.client().get('/categories/'+category_id+'/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['current_category'],category_id)

    def test_random_question_game(self):
        res = self.client().post('/quizzes',json={'quiz_category':'1','previous_questions':'[]'})
        data= json.loads(res.data)
        self.assertEqual(res.status_code , 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['question']['category'],'1')
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
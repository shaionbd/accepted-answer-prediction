# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import randint

import datetime
import os
import pandas as pd
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from acceptance_answers.templates.library.sentimentFromComment import Sentiment
from acceptance_answers.templates.library.AcceptancePrediction import AcceptancePrediction

def index(request):
    return render(request, "views/pages/home.html")

def answers(request):
    if request.method == 'POST':
        # get url from input
        url = request.POST['url']
        # split url string to array
        chunk = url.split("/")
        # get question id
        question_id = 0
        for i in range(len(chunk)):
            if chunk[i] == 'questions':
                question_id = chunk[i+1]
                break

        # call api to get question with answers
        question_url = "https://api.stackexchange.com/2.2/questions/"+question_id+"?order=asc&sort=votes&site=stackoverflow&filter=!)E0gjB54xbAxpoTEYegvUW4WzaEaTqPbbLj6fHpmonX)zoKR1";
        question_response = requests.get(question_url)
        question_data = question_response.json()
        data = question_data['items']


        # question info
        all_answers = data[0]['answers']
        body = data[0]['body']
        title = data[0]['title']
        answer_count = data[0]['answer_count']


        # try to catch all the question information
        try:
            accepted_answer_id = data[0]['accepted_answer_id']
        except:
            accepted_answer_id = 0

        try:
            question_score = data[0]['score']
        except:
            question_score = 0

        try:
            question_view_count = data[0]['view_count']
        except:
            question_view_count = 0

        try:
            question_comment_count = data[0]['comment_count']
        except:
            question_comment_count = 0

        try:
            question_favorite_count = data[0]['favorite_count']
        except:
            question_favorite_count = 0

        question_creation_date = data[0]['creation_date']

        tags = data[0]['tags']
        owner = data[0]['owner']['user_id']

        # parse data for model
        q_answers = []
        temp_comments = {}

        QuestionId = []
        AcceptedAnswerId = []
        QuestionScore = []
        QuestionViewCount = []
        Question = []
        QuestionCreationDate = []
        QuestionOwnerUserId = []
        Title = []
        Tags = []
        AnswerCount = []
        QuestionCommentCount = []
        QuestionFavoriteCount = []
        AnswerId = []
        AnswerScore = []
        Answer = []
        AnswerCreationDate = []
        AnswerOwnerUserId = []
        AnswerCommentCount = []
        CommentId = []
        CommentScore = []
        Comment = []
        CommentCreationDate = []
        CommentUserId = []

        # parse comments of answers for sentiment analysis
        for answer in range(len(all_answers)):
            answer_id = str(all_answers[answer]["answer_id"])
            comment_url = "https://api.stackexchange.com/2.2/answers/"+answer_id+"/comments?order=desc&sort=votes&site=stackoverflow&filter=!9YdnSNN7R";
            comment_response = requests.get(comment_url)
            comment_data = comment_response.json()
            try:
                comments = comment_data['items']
            except:
                comments = {}

            acceptance_probability = 0
            not_acceptance_probability = 0


            # to do nlp tools
            i = 0
            for comment in range(len(comments)):
                # temp_comments.append({"QuestionOwnerUserId": 1234, "AnswerOwnerUserId": 234, "CommentUserId": 345})
                QuestionId.append(question_id)

                # QuestionId[i] = question_id
                AcceptedAnswerId.append(accepted_answer_id)
                QuestionScore.append(question_score)
                QuestionViewCount.append(question_view_count)
                Question.append(body)
                QuestionCreationDate.append(datetime.datetime.fromtimestamp(question_creation_date).strftime('%m/%d/%Y %H:%M'))
                QuestionOwnerUserId.append(owner)
                Title.append(title)
                Tags.append(tags)
                AnswerCount.append(answer_count)
                QuestionCommentCount.append(question_comment_count)
                QuestionFavoriteCount.append(question_favorite_count)
                try:
                    AnswerId.append(all_answers[answer]['answer_id'])
                except:
                    AnswerId.append(0)
                try:
                    AnswerScore.append(all_answers[answer]['score'])
                except:
                    AnswerScore.append(0)
                try:
                    Answer.append(all_answers[answer]['body'])
                except:
                    Answer.append("")
                AnswerCreationDate.append(datetime.datetime.fromtimestamp(all_answers[answer]['creation_date']).strftime('%m/%d/%Y %H:%M'))
                try:
                    AnswerOwnerUserId.append(all_answers[answer]['owner']['user_id'])
                except:
                    AnswerOwnerUserId.append(0)
                try:
                    AnswerCommentCount.append(all_answers[answer]['comment_count'])
                except:
                    AnswerCommentCount.append(0)
                try:
                    CommentId.append(comments[comment]['comment_id'])
                except:
                    CommentId.append(0)
                try:
                    CommentScore.append(comments[comment]['score'])
                except:
                    CommentScore.append(0)

                Comment.append(comments[comment]['body'])
                CommentCreationDate.append(datetime.datetime.fromtimestamp(comments[comment]['creation_date']).strftime('%m/%d/%Y %H:%M'))
                try:
                    CommentUserId.append(comments[comment]['owner']['user_id'])
                except:
                    CommentUserId.append(0)
                i += 1

            # for view
            q_answers.append({
                "body": all_answers[answer]['body'],
                "score": all_answers[answer]['score'],
                "is_accepted": all_answers[answer]['is_accepted'],
                "body_markdown": all_answers[answer]['body_markdown'],
                "answer_id": all_answers[answer]['answer_id'],
                "comments": comments,
                "acceptance_probability": acceptance_probability,
                "not_acceptance_probability": not_acceptance_probability
            })

            # for acceptance probability
            temp_comments = pd.DataFrame({
                'QuestionId': QuestionId,
                'AcceptedAnswerId': AcceptedAnswerId,
                'QuestionScore': QuestionScore,
                'QuestionViewCount': QuestionViewCount,
                'Question': Question,
                'QuestionCreationDate': QuestionCreationDate,
                'QuestionOwnerUserId': QuestionOwnerUserId,
                'Title': Title,
                'Tags': Tags,
                'AnswerCount': AnswerCount,
                'QuestionCommentCount': QuestionCommentCount,
                'QuestionFavoriteCount': QuestionFavoriteCount,
                'AnswerId': AnswerId,
                'AnswerScore': AnswerScore,
                'Answer': Answer,
                'AnswerCreationDate': AnswerCreationDate,
                'AnswerOwnerUserId': AnswerOwnerUserId,
                'AnswerCommentCount': AnswerCommentCount,
                'CommentId': CommentId,
                'CommentScore': CommentScore,
                'Comment': Comment,
                'CommentCreationDate': CommentCreationDate,
                'CommentUserId': CommentUserId

            })

        BASE = os.path.dirname(os.path.abspath(__file__))
        #
        # temp_comments.to_csv(BASE + '/templates/library/cc.csv', index=False)
        # temp_comments = pd.read_csv(BASE+"/templates/library/cc.csv", dtype='unicode')

        # get sentiment analysis data from nlk tools
        df_sentiment = Sentiment.commentSentiment(temp_comments)

        # predict answers acceptance percentage whether the answer will accept or not
        predict = AcceptancePrediction.prediction(BASE, df_sentiment)

        # parse data for view
        for answer in range(len(q_answers)):
            for id in range(len(predict)):
                if predict['AnswerId'][id] == q_answers[answer]['answer_id']:
                    q_answers[answer]['acceptance_probability'] = predict['AcceptPrediction'][id]
                    q_answers[answer]['not_acceptance_probability'] = 100 - int(predict['AcceptPrediction'][id])
                    break

        # answers is sorted by acceptance probabilty
        q_answers.sort(key=lambda x: x['acceptance_probability'], reverse=True)
        content = {"body": body, "question_url": url, "title": title, "question_score": question_score, "question_favorite_count": question_favorite_count, "answer_count": answer_count, "answers": q_answers}
        # render view with all data
        return render(request, "views/pages/question.html", content)
    else:
        return HttpResponseRedirect('/')
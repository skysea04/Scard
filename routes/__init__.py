from flask import Blueprint
from models.model import Comment, CommentUserLike, Post, PostBoard, PostUserLike, User, Scard, Messages, Collage, CollageDepartment, Subscribe, cache, db
page = Blueprint('page', __name__)

from . import post, user, message
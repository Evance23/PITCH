from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from .forms import UpdateProfile
# from .. import db
from .. import db, photos
from flask import Blueprint 

from .forms import PostForm, CommentForm, UpdateProfile
from ..models import Post, Comment, User, Upvote, Downvote

main = Blueprint('main', __name__) 


@main.route('/') 
def index():
    pitches = Post.query.all()


    art = Post.query.filter_by(category='art').all()
    music = Post.query.filter_by(category='music').all()
    poetry = Post.query.filter_by(category='poetry').all()
    
    return render_template('index.html',pitches=pitches, art=art, music=music, poetry=poetry)

@main.route('/art')
def art():
    arts =  Post.query.filter_by(category='art').all()
    print(arts)
    return render_template("art.html", arts=arts)


@main.route('/music')
def music():
    music = Post.query.filter_by(category='music').all()
    return render_template ("music.html", music=music)

@main.route('/poetry')
def poetry():
    poetries = Post.query.filter_by(category='poetry').all()
    return render_template("poetry.html", poetries=poetries) 
    


    
@main.route('/posts')
@login_required
def posts():
    posts = Post.query.all()
    likes = Upvote.query.all()
    user = current_user
    return render_template('pitch_display.html', posts=posts, likes=likes, user=user)


@main.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        post = form.post.data
        category = form.category.data
        user_id = current_user._get_current_object().id
        post_obj = Post(post=post, title=title,
                        category=category, user_id=user_id)
        post_obj.save()
        return redirect(url_for('main.index'))
    return render_template('pitch.html', form=form)


@main.route('/user/<uname>/update/pic', methods=['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username=uname).first()
    if 'photo' in requests.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile', uname=uname))


@main.route('/comment/<int:post_id>', methods=['GET', 'POST'])
@login_required
def comment(post_id):
    form = CommentForm()
    post = Post.query.get(post_id)
    user = User.query.all()
    comments = Comment.query.filter_by(post_id=post_id).all()
    if form.validate_on_submit():
        comment = form.comment.data
        post_id = post_id
        user_id = current_user._get_current_object().id
        new_comment = Comment(
            comment=comment,
            post_id=post_id,
            user_id=user_id
        )
        new_comment.save()
        new_comments = [new_comment]
        print(new_comments)
        return redirect(url_for('.comment', post_id=post_id))
    return render_template('comment.html', form=form, post=post, comments=comments, user=user)


@main.route('/user')
@login_required
def user():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    if user is None:
        return ('not found')
    return render_template('profile.html', user=user)


@main.route('/user/<name>/update_profile', methods=['POST', 'GET'])
@login_required
def updateprofile(name):
    form = UpdateProfile()
    user = User.query.filter_by(username=name).first()
    if user is None:
        error = 'The user does not exist'
    if form.validate_on_submit():
        user.bio = form.bio.data
        user.save()
        return redirect(url_for('.profile', name=name))
    return render_template('profile/update_profile.html', form=form)


@main.route('/like/<int:id>', methods=['POST', 'GET'])
@login_required
def upvote(id):
    post = Post.query.get(id)
    new_vote = Upvote(post=post, upvote=1)
    new_vote.save()
    return redirect(url_for('main.posts'))


@main.route('/dislike/<int:id>', methods=['GET', 'POST'])
@login_required
def downvote(id):
    post = Post.query.get(id)
    nv = Downvote(post=post, downvote=1)
    nv.save()
    return redirect(url_for('main.posts'))

# Messaging Backend API
### built using Django

With this backend, you can use the following API endpoints to create and delete users. Have users create new posts with images and text and create comments to user posts. Images are stored using [AWS S3](https://aws.amazon.com/s3/). This can be used for a rudimentary messaging or social media application. All URL inputs and outputs are require and return JSON objects.

The project uses a json file holding the projects secret key and other project level variables used in the settings.py file. For obvious reasons this file is not commited with the project. You will need to create your own.


* Base URL for user authorization = **__/snaplife/api/auth/__**
* Base URL for user = **__/snaplife/api/user/__**
* Base URL for post = **__/snaplife/api/user/posts/__**
* Base URL for comment = **__/snaplife/api/user/posts/comment/__**
* _NOTE: All URL endpoints need to end with a forward slash_


### User authorization
| Endpoint| Method | Required input | Results |
|---------|--------|----------------|---------|
| user/login/ | POST | <ul><li>'username': the users unique username</li><li>'password': the users password</li></ul>| 'userid': the users unique user ID |
| user/logoff/ | POST | <ul><li>'userid': the users inque user ID</li></ul> | 'message': success if successfull |
| user/create/ | POST | <ul><li>'username': must be unique</li><li>'password': this is stored as a cryptographic hash</li><li>'firstname': users first name</li><li>'lastname': users last name</li><li>'email': the uers email (optional)</li><li>'about': Short bio for the user less than 255 characters (optional)</li><li>'profilepic': base64 encoded picture (optional)</li></ul> | 'userid': the user ID for the new user |
| user/delete/ | POST | <ul><li>'username': the users username</li><li>'password': the users password (user must verify by password before user is deleted)</li></ul> | 'message': success if successfull |

### User
| Endpoint | Method | Required input | Results |
|----------|--------|----------------|---------|
| /count/(userid)/(count_type)/ | GET | userid: the users unique user id <li>count_type: posts = return the number of posts the user has made</li><li>count_type: followers = return the number of followers</li><li>count_type: following = return the number of people the user is following</li> | <li>'count': the count number</li> |
| /profile/update/ | POST | <li>'userid': the users unique user id</li><li>'profilepic': a base64 encode image</li> | <li>'message': success if successfull</li><li>'url': the url of the new image that can be used inside an image tag</li> |
| /follow/new/ | POST | <li>'userid': the users unique user id</li><li>'username': the username the user wants to start following</li> | <li>'message': success if successfull</li><li>'followercount': the users new following count</li> |
| /follow/remove/ | POST | <li>'userid': the users unique user id</li><li>'username': the username the user no longer wants to follow</li> | <li>'message': success if successfull</li><li>'followercount': the users new following count</li> |
| <dd>/description/(userid)/</dd><dd>/description/</dd> | <dd>GET</dd><dd>POST</dd> | <li>'userid': the unique user id</li><li>'description': the new description less than 255 characters</li> | <li>GET: returns the description</li><li>POST: 'message': success if the description was updated</li> |

## Posts
| Endpoint | Method | Required input | Results |
|----------|--------|----------------|---------|
| /create/ | POST | <li>'userid': the users unique user id</li><li>'image': a base64 encode image for the post</li><li>'message': the message for the post</li><li>'title': the post title</li> | post object<li>'postid': the unique id for the created post</li><li>'message': the post message</li><li>'title': the post title</li><li>'views': the post view count</li><li>'likes': the post like count</li><li>'imageurl': the url for the post image</li><li>'date': the post creation date</li> |
| /delete/ | POST | You can delete a post by providing the post id or the post title<li>'userid': the users unique user id</li><li>'postid': the posts unique id</li><li>'title': the title of the post</li> | <li>'message': success if successfull</li><li>'postcount': the new count of the number of user posts</li> |
| /update/ | POST | <li>'userid': the users unique user id</li><li>'postid': the unique post id that needs to be updated</li><li>'title': update to the post title (optional)</li><li>'message': update to the post message (optional)</li> | post object<li>'postid': the post id</li><li>'message': post message</li><li>'title': the post title</li><li>'views': the post view count</li><li>'likes': the like count</li><li>'imageurl': the post image url</li><li>'date': the post creation date</li>|
| /report/ | POST | <li>'postid': the unique post id that is being reported</li><li>'reason': the reason (message) post is being reported</li><li>'email': the email of the reporter</li> | an email will be sent<li>'message': success</li><li>'count': the report count</li> |
| /comment/count/(post_id)/ | GET | <li>'post_id': the unique post id to get the comment count</li> | <li>'message': success if successfull</li><li>'count': the comment count</li><li>'commentids': a list of the comment unique ids</li>
| /search/title/(user_id)/(title)/(count)/ | GET | <li>user_id: the posts from this user id</li><li>title: search posts containing this title</li><li>count: return this many found posts</li> | 'post': list of post objects as follows<li>'postid': unique post id</li><li>'message': post message</li><li>'title': post title</li><li>'views': post view count</li><li>'likes': post like count</li><li>'imageurl': url to the post image </li><li>'date': the post creation date</li>|
| /search/range/(user_id)/(time_stamp)/(count)/ | GET | <li>user_id: the posts from this user id</li><li>time_stamp: search from this date. use `datetime.timestamp()`</li><li>count: return this many posts</li> |'post': list of post objects as follows<li>'postid': unique post id</li><li>'message': post message</li><li>'title': post title</li><li>'views': post view count</li><li>'likes': post like count</li><li>'imageurl': url to the post image </li><li>'date': the post creation date</li>
| <dd>/like/(post_id)/</dd><dd>/like/</dd> | <dd>GET</dd><dd>POST</dd> | <li>post_id: the post id</li><li>{ 'postid': the post id to like</li><li>'userid': the user who is liking the post }</li> | <li>'message': success if successfull</li><li>'likecount': the posts new like count</li> |

## Comments
| Endpoint | Method | Required input | Results |
|----------|--------|----------------|---------|
| /create/ | POST | <li>'postid': the unique post id to attach the comment to</li><li>'userid': the unique user id who is creating the comment</li><li>'message': the comment</li> | <li>'message': success if successfull</li><li>'commentid': the unique id for the created comment</li> |
| /delete/ | POST | <li>'userid': the unique user id (the owner of the comment)</li><li>'commentid': the unique comment id we are deleting</li> | <li>'message': success if successfull</li><li>'commentid': the unique comment id of the comment that was deleted</li> |
| <dd>/count/like/(comment_id)/</dd><dd>/count/like/</dd> | <dd>GET</dd><dd>POST</dd> | GET<li>'comment_id': the unique comment id</li>POST<li>'userid': the userid who is liking the comment</li><li>'commentid': the unique comment ID the user wants to like</li> | <li>'count': the like count</li>

### Copyright(c) 2017 Joe Berria
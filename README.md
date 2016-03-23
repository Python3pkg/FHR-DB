FHR DB
======
Inspired from the blog post http://backchannel.org/blog/friendfeed-schemaless-mysql ,FHR DB is just a programmed Layer which enables a MYSQL Database as NOSQL Database. I skipped some optimizations, which are discussed in the blog, for better usage in mysql console. I plan to implement these optimizations, but then a kind of "PhpMyAdmin" for FHR DB is needed, cause if the Datafield is zipped or if we have binary ID, mysql console is just useless.

Why FHR DB?
-----------
During creating an application, you need to create new database fields or delete someone. With FHR DB, you only have to change something at the DB if you want to make this fields searchable. With the FHR DB you can only query indices, that prevents you from coding a slow applications, and provides a lot of flexibility. If you have a mass of data you could easily create new indices on the fly, on a running database, with no perfomance impact. The index will be immediately up, for all new entities, for all old you just need to run the cleaner.

How to install
--------------
Install it via pip

    pip install fhr-db

How to use it
-------------
It's a litte bit like Google Big Table. If you want to create an User Model, the table you have to create looks like this

    CREATE TABLE `users` (
      `id` INT(22) NOT NULL auto_increment,
      `body` TEXT NOT NULL,
      `updated` TIMESTAMP NOT NULL,
      `created` TIMESTAMP NOT NULL,
      PRIMARY KEY  (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

In the body the json representation of the User is created. In your code you define the User Model like this.

    class User(Model):
        table = 'users'
        fields = {'nickname' : None, 'password' : None, 
                  'email' : { 'confirmed' : False, 'token' : None, 'email' : None, 'sent': False }}

You can save and get the UserModel like this

    user = User({'nickname' : 'notstandard', 'email.email' : 'kordulla@googlemail.com')
    user.set(password='Another way to set sometgin')
    user.set(email__confirmed=True)
    user.set(email__token='Asd',sent=True)
    user.put()
    print(user.get('id')) # prints out user id for this saved user.

You can set the values in the constructor, there a dict in dict is seperated through the `.`, in the set command it's seperated through `__`. To get the user with id=10 just use this code

    user = User.fqlGet("id = %s", 10)
    if user is not None:
        print(user.get('id')) # just prints out 10 then if user was found

If you want to query the user with nickname test you have to create an Index. The table for the index nickname look like this

    CREATE TABLE `index_nickname_users` (
      `id` INT(22) NOT NULL auto_increment,
      `nickname` VARCHAR(64) NOT NULL,
      `user_id` INT(22) NOT NULL UNIQUE,
      PRIMARY KEY  (`id`),
      KEY (`nickname`, `user_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

And the updated model like this.

    class User(Model):
        table = 'users'
        fields = {'nickname' : None, 'password' : None.
                  'email' : { 'confirmed' : False, 'token' : None, 'email' : None, 'sent': False }}
        indices = [ Index(['nickname'], 'index_nickname_users', 'user_id')]

So the code to query a single User for a nickname is then.

    user = User.fqlGet("nickname = %s", test)

For more than one expected result like in this case, cause nickname is not really unique use

    user = User.fqlAll("nickname = %s", test)

If you had already users save to the database their nickname index wouldn't be built so they wouldn't appear in the results. To built their index just use the cleaner

    cleaner = Cleaner()
    cleaner.cleanModel(User)

or if you have more than one index for a specific index use

    cleaner = Cleaner()
    cleaner.cleanModel(User. User.indices[0])

to just update the index[0].

Test Driven Development
-----------------------
For quality insurance I coded the whole FHR DB with test driven development. For 300 lines of code, I created 80 testcases, which should cover all code atm. If you find a bug just make a pull request with the testcase, which reproduce the bug.

What to do in the future
------------------------
If you like this concept it would be nice, if you can help to get FHR DB growing. What we needed, is that we perhaps could easily run the cleaner from command like ./clean.sh modelfile namespaceofmodel . It would be nice that index table will be automatically created from a model file, build the index etc, just with one command. For better performance binary index, and zipped json would be cool, but for that we need a data discover tool, like e.g. PhpMyAdmin for FHR DB, because the mysql console will be useless with binary id or zipped jsons.

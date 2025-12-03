
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.post import Post
from app.models.user import User
from app.models.setting import Setting
from app.models.plugin import Plugin
from app.models.theme import Theme
# Try to import FriendLink, handle if plugin not present or import fails
try:
    from plugins.friend_links.models import FriendLink
except ImportError:
    FriendLink = None

app = create_app()

def check_paths():
    with app.app_context():
        print("Checking User avatars:")
        users = User.query.filter(User.avatar.isnot(None)).all()
        if not users:
            print("No users with avatars found.")
        for user in users:
            print(f"User {user.username}: {repr(user.avatar)}")

        print("\nChecking Post featured images:")
        posts = Post.query.filter(Post.featured_image.isnot(None)).all()
        if not posts:
            print("No posts with featured images found.")
        for post in posts:
            print(f"Post {post.title}: {repr(post.featured_image)}")

        print("\nChecking Settings (logo/icon):")
        settings = Setting.query.filter(Setting.key.in_(['site_logo', 'site_icon', 'favicon'])).all()
        if not settings:
            print("No settings found for logo/icon.")
        for setting in settings:
            print(f"Setting {setting.key}: {repr(setting.value)}")

        print("\nChecking Plugins install_path:")
        plugins = Plugin.query.all()
        if not plugins:
            print("No plugins found.")
        for plugin in plugins:
            # Access the raw column value
            raw_path = db.session.query(Plugin._install_path).filter(Plugin.id == plugin.id).scalar()
            print(f"Plugin {plugin.name}: {repr(raw_path)}")

        print("\nChecking Themes install_path and screenshot:")
        themes = Theme.query.all()
        if not themes:
            print("No themes found.")
        for theme in themes:
            raw_path = db.session.query(Theme._install_path).filter(Theme.id == theme.id).scalar()
            print(f"Theme {theme.name} install_path: {repr(raw_path)}")
            print(f"Theme {theme.name} screenshot: {repr(theme.screenshot)}")

        if FriendLink:
            print("\nChecking FriendLink logos:")
            links = FriendLink.query.filter(FriendLink.logo.isnot(None)).all()
            if not links:
                print("No friend links with logos found.")
            for link in links:
                print(f"FriendLink {link.name}: {repr(link.logo)}")
        else:
            print("\nFriendLink model not available.")


if __name__ == '__main__':
    check_paths()

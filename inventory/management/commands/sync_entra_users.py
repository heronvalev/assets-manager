from django.core.management.base import BaseCommand
from inventory.models import EntraUser
from inventory.graph_api import get_all_users

class Command(BaseCommand):
    help = "Sync Entra users from Microsoft Graph API into the local database"

    def handle(self, *args, **options):
        """
        Queries Microsoft Graph for all users and updates the local EntraUser table.
        """
        # Fetch all users
        users = get_all_users()

        # Extract user data for each user to insert into the DB
        for user_data in users:
            entra_user_id = user_data.get("id")
            upn = user_data.get("userPrincipalName")
            display_name = user_data.get("displayName", "Unavailable")
            department = user_data.get("department", "Unavailable")
            is_active = user_data.get("accountEnabled")

            # Update or create the user in the DB
            EntraUser.objects.update_or_create(
                entra_user_id=entra_user_id,
                defaults={
                    "upn": upn,
                    "display_name": display_name,
                    "department": department,
                    "is_active": is_active,
                    }
            )

        # Get the set of EntraUser IDs returned from Microsoft Graph
        current_ids = {user_data["id"] for user_data in users}

        # Delete any EntraUser objects not in current_ids
        EntraUser.objects.exclude(entra_user_id__in=current_ids).delete()


        self.stdout.write(self.style.SUCCESS("Entra users synced successfully."))

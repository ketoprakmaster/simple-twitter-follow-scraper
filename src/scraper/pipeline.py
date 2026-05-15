from scraper.driver import TwitterDriver
from common.exceptions import UserRecordsNotExists
from common.types import MODE, ComparisonResults, UserStatus
from models.users import UserRecords, UserSnapshot


class ScraperPipeline:
    def __init__(self, headless: bool = True, mode: MODE = MODE.following):
        self.mode = mode
        self.headless = headless
        self.username : str
        self.history : UserRecords
        self.driver = TwitterDriver(headless, mode)

    async def run(self) -> ComparisonResults:
        """The main sequence: Scrape -> Compare -> Verify -> Save"""
        # Fetch live data
        scraped_users = await self.driver.scrape_user_follows()
        current_snap = UserSnapshot(self.driver.username, self.driver.mode, scraped_users)

        try:
            past_snap = self.history[-1]
            results = current_snap - past_snap
        except UserRecordsNotExists:
            # First time scraping this user/mode
            results = ComparisonResults(added=scraped_users)
            current_snap.save()
            return results

        # Verify potential "unfollows"
        if results.removed:
            await self._verify_and_fix_results(results, current_snap)

        # Save if the world has actually changed
        if results.has_actual_changes:
            current_snap.save()

        return results

    async def initialize(self) -> None:
        # initialize the driver
        await self.driver.initialize_driver()
        # get the users info
        await self.driver.get_user_handle()

        self.username = self.driver.username
        self.history = UserRecords(self.username, self.mode)

    async def _verify_and_fix_results(self, results: ComparisonResults, current: UserSnapshot):
        """Cross-references removals with live status to filter out scraper errors."""
        await results.check_status(driver=self.driver)

        # Identify users the scraper missed but still exist
        false_negatives = {
            user for user, status in results.removed.items()
            if status in {UserStatus.EXISTS, UserStatus.WITHHELD}
        }

        if false_negatives:
            # Fix the current snapshot so the 'missing' users are back in
            current.users.update(false_negatives)
            # Remove them from the 'removed' list in results
            for user in false_negatives:
                del results.removed[user]

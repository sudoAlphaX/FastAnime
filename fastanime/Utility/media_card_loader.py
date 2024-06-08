from kivy.cache import Cache
from kivy.logger import Logger
from pytube import YouTube

from ..libs.anilist.anilist_data_schema import AnilistBaseMediaDataSchema
from ..Utility import anilist_data_helper, user_data_helper

Cache.register("trailer_urls.anime", timeout=360)


class MediaCardDataLoader(object):
    """this class loads an anime media card and gets the trailer url from pytube"""

    def media_card(
        self,
        anime_item: AnilistBaseMediaDataSchema,
    ):
        media_card_data = {}
        media_card_data["anime_id"] = anime_id = anime_item["id"]

        # TODO: ADD language preference
        if anime_item["title"].get("romaji"):
            media_card_data["title"] = anime_item["title"]["romaji"]
        else:
            media_card_data["title"] = anime_item["title"]["english"]

        media_card_data["cover_image_url"] = anime_item["coverImage"]["medium"]

        media_card_data["popularity"] = str(anime_item["popularity"])

        media_card_data["favourites"] = str(anime_item["favourites"])

        media_card_data["episodes"] = str(anime_item["episodes"])

        if anime_item.get("description"):
            media_card_data["description"] = anime_item["description"]
        else:
            media_card_data["description"] = "None"

        # TODO: switch to season and year
        #
        media_card_data["first_aired_on"] = (
            f'{anilist_data_helper.format_anilist_date_object(anime_item["startDate"])}'
        )

        media_card_data["studios"] = anilist_data_helper.format_list_data_with_comma(
            [
                studio["name"]
                for studio in anime_item["studios"]["nodes"]
                if studio["isAnimationStudio"]
            ]
        )

        media_card_data["producers"] = anilist_data_helper.format_list_data_with_comma(
            [
                studio["name"]
                for studio in anime_item["studios"]["nodes"]
                if not studio["isAnimationStudio"]
            ]
        )

        media_card_data["next_airing_episode"] = "{}".format(
            anilist_data_helper.extract_next_airing_episode(
                anime_item["nextAiringEpisode"]
            )
        )
        if anime_item.get("tags"):
            media_card_data["tags"] = anilist_data_helper.format_list_data_with_comma(
                [tag["name"] for tag in anime_item["tags"]]
            )

        media_card_data["media_status"] = anime_item["status"]

        if anime_item.get("genres"):
            media_card_data["genres"] = anilist_data_helper.format_list_data_with_comma(
                anime_item["genres"]
            )

        if anime_id in user_data_helper.get_user_anime_list():
            media_card_data["is_in_my_list"] = True

        if anime_item["averageScore"]:
            stars = int(anime_item["averageScore"] / 100 * 6)
            media_card_data["stars"] = [0, 0, 0, 0, 0, 0]
            if stars:
                for i in range(stars):
                    media_card_data["stars"][i] = 1

        if trailer := anime_item.get("trailer"):
            trailer_url = "https://youtube.com/watch/v=" + trailer["id"]
            media_card_data["_trailer_url"] = trailer_url
        else:
            media_card_data["_trailer_url"] = ""
        return media_card_data

    def get_trailer_from_pytube(self, trailer_url, anime):
        if trailer := Cache.get("trailer_urls.anime", trailer_url):
            return trailer
        try:
            yt = YouTube(trailer_url)
            trailer = yt.streams.filter(
                progressive=True,
                file_extension="mp4",
            )[-1].url
            Logger.info(f"Pytube Success:For {anime}")
            Cache.append("trailer_urls.anime", trailer_url, trailer)
            return trailer
        except Exception as e:
            Logger.error(f"Pytube Failure:For {anime} reason: {e}")
            return ""


media_card_loader = MediaCardDataLoader()

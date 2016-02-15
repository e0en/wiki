import image
import misc
import misc_markdown


mapping = {
    'img': image.parse,
    'backlinks': misc.backLinks,
    'redirect': misc.redirectTo,
}

mapping_markdown = {
    'img': image.parse_markdown,
    'backlinks': misc_markdown.backLinks,
    'redirect': misc_markdown.redirectTo,
}

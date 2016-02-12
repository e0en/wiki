import image
import misc

mapping = {
    'img': image.parse,
    'backlinks': misc.backLinks,
    'redirect': misc.redirectTo,
}

mapping_markdown = {
    'img': image.parse_markdown,
    'backlinks': misc.backLinks,
    'redirect': misc.redirectTo,
}

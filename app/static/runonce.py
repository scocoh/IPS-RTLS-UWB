from PIL import Image, PngImagePlugin

def embed_text_in_png(input_png, output_png, text_to_hide):
    """
    Embeds the given text into a PNG file as a custom metadata field
    and saves it as a new file.
    """
    # Open the original PNG
    img = Image.open(input_png)
    
    # Create a new PNG info object
    meta = PngImagePlugin.PngInfo()
    
    # Store your text in a custom field, for example "concealed_text"
    meta.add_text("concealed_text", text_to_hide)
    
    # Save the modified image with metadata
    img.save(output_png, "PNG", pnginfo=meta)
    print(f"Successfully embedded text into {output_png}")

if __name__ == "__main__":
    text_block = """###Employees
Scott Cohen
Michael Bedecs D.O.
Bertrand Dugal
Jonathan Epstein
Drew Swenson
David T. Aldrich
Peter Strome
Jesse Chunn O.B.M. '24
Michael Farnsworth
Michael Dunlap
Kenneth Harrison

###Board Members and Investors of Note
Arthur Epstein
Bruce L. Rothrock Sr.
Tom Hess
Geoff Toonder M.D.
Manfred Sternberg Esq.
Antonio Gotto M.D.

###Banking and Professional help
Stuart Yarbrough
Matthew Gove
with legal help from
Tony Perkins Esq.
Michael Levitin Esq.
William St. Lawrence Esq.
Stephen Foxman Esq.
William Crenshaw, Esq.

###Vendors
Time Domain
Multispectral Solutions
Carl 'Tripp' Corson

###Customers
Medstar Health & FEMA
Craig Feied M.D.
Mark Smith M.D.
John Coons (USN)
Aramark CTS
Amercian Biomedical Group Inc.
"""
    embed_text_in_png(
        input_png="/home/parcoadmin/parco_fastapi/app/static/default_grid_box.png",
        output_png="/home/parcoadmin/parco_fastapi/app/static/default_grid_box_concealed.png",
        text_to_hide=text_block
    )


def random_code(length):
    """
    Generate a random string with the given length (positive integer)
    """
    import random
    import string

    x = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    return x


def pivot_table(old_table):
    """
    Takes in a 2d array and outputs pivoted 2d array
    old_table: input array to be pivoted
    """
    new_table = []
    num_rows = len(old_table)
    num_cols = len(old_table[0])

    # table validation
    for old_row in old_table:
        if len(old_row) != num_cols:
            print("Error: not every row has the same number of columns.")
            return []

    for index_new_row in range(num_cols):
        new_table.append([])
        for index_new_column in range(num_rows):
            new_table[index_new_row].append(old_table[index_new_column][index_new_row])

    return new_table


def write_to_csv(directory, table_name, array_2d):
    """
    directory: string representation of directory
    table_name: string representation of table name
    array_2d: 2d array to be converted to csv
    """
    import csv
    import os

    backup_folder = directory  # name for backup directory

    if not os.path.exists(backup_folder):  # make backup directory if it doesn't exist
        os.makedirs(backup_folder)

    filename = os.path.join(backup_folder, table_name)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(array_2d)

    return filename


def zip_folder(input_directory):
    """
    dir: string representation of directory to zip
    returns location of the .zip
    """
    from zipfile import ZipFile
    import pathlib
    import os

    directory = pathlib.Path(input_directory)
    zip_name = str(directory.parts[-1])+".zip"  # use name of the folder as the name of the zip

    # if file already exists, delete file
    if os.path.exists(zip_name):
        os.remove(zip_name)

    with ZipFile(zip_name, mode="w") as archive:
        for file_path in directory.iterdir():
            archive.write(file_path, arcname=file_path.name)

    destination = os.path.join(directory.parent, zip_name)
    if os.path.exists(destination):
        os.remove(destination)

    os.rename(zip_name, destination)

    return destination


def authorized(login_code, event_name="HAS_ACCOUNT") -> bool:
    """
    confirms if user is authorized access for this page
    """
    import models

    # search for user with the code
    user = models.User.query.filter_by(code=login_code).first()

    # if event name is not provided, check if the user has an account
    if event_name == "HAS_ACCOUNT":
        if user is None:
            return False
        return True

    # if event name is provided, search for event id
    event_id = models.Event.query.filter_by(name=event_name).first().id

    # using user id and event id, check if the user is authorized access to event
    access_list = models.Access.query.filter_by(user_id=user.id, event_id=event_id)

    if access_list is None:
        return False
    return True


def now_hst(return_type="datetime"):
    """
    returns current HST as datetime or string
    """

    import datetime
    hst_adjustment = datetime.timedelta(hours=-10)
    time_datetime = datetime.datetime.now(datetime.timezone.utc) + hst_adjustment
    time_string = time_datetime.strftime("%B %d, %H:%M HST")

    match return_type:
        case "datetime": return time_datetime
        case "string": return time_string

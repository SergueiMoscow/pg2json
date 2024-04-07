## Backup and Restore PostgreSQL Tables in JSON Format.

### Configuration
Configuration file - `config.json`

#### File Structure:
At the top level, there is an array (list) of applications. It is assumed that all databases of one application have an identical structure but are located on different servers (in different databases, in different schemas).

Each application has the following properties:
* `application` - application name
* `databases` - list (array) of databases
* `backup_dir` - directory where backup copies will be saved and from where they will be restored

A separate directory with the application name is created inside the `backup_dir` for each application, allowing the same directory to be used for all applications.
* `tables` (optional) - list of tables to be processed (saved or restored)

In the GUI, this list can be modified by selecting the necessary tables.

Structure of the database object:
* `dsn` - URI
* `schema` - schema in the PostgreSQL database
* `options`
`ignore_unique_violations` - for restoration - ignore the attempt to insert an already existing key. This is useful when adding data from the server to the backup copy.

### Launching the GUI Interface:
To launch the GUI interface, use the command `python main.py`.
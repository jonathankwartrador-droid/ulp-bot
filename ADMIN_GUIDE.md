# Admin Guide

## Adding Admin Access

Edit `config.json` and add your Telegram user ID to the `admin_ids` array:

```json
{
  "admin_ids": [123456789, 987654321]
}
```

To find your user ID, use `/start` and check the output.

## Admin Commands

### User Management

```bash
# Add credits to user
/addcredits <user_id> <amount>

# Remove credits from user
/removecredits <user_id> <amount>

# Ban a user
/banuser <user_id>

# Unban a user
/unbanuser <user_id>
```

### Inventory Management

```bash
# Add new inventory file
/addinventory /path/to/file.txt

# Remove inventory file
/removeinventory filename.txt

# Reload all inventory files
/reload

# Clean up inventory file (remove duplicates, empty lines)
/cleaninventory filename.txt

# Validate inventory file
/validateinventory filename.txt
```

### Admin Panel

```bash
# Open admin dashboard
/admin

# View user management options
/users

# View inventory management options
/inventory
```

## Managing Inventory Files

### Adding Files

1. Place your `.txt` files in the `inventory/` directory
2. Run `/reload` to load them
3. Verify with `/inventory` command

### File Format

Each line in your `.txt` file should be:

```
URL:LOGIN:PASSWORD
```

Examples:
```
authenticate.riotgames.com:username:password
https://example.com:user@email.com:pass123
android://token@app.com/:user:pass
```

### File Validation

```bash
/validateinventory myfile.txt
```

This will show:
- Total lines
- Valid records
- Invalid records
- Empty lines
- Validity percentage
- Sample invalid lines

### Cleaning Up Files

```bash
/cleaninventory myfile.txt
```

This will:
- Remove empty lines
- Remove duplicate records
- Remove malformed lines
- Save cleaned version

## Managing Users and Credits

### View User Profile

```bash
/profile
```

### Add Credits

```bash
/addcredits 123456789 100
```

Gives 100 credits to user 123456789

### Remove Credits

```bash
/removecredits 123456789 50
```

Removes 50 credits from user 123456789

### Ban/Unban Users

```bash
# Ban user
/banuser 123456789

# Unban user
/unbanuser 123456789
```

Banned users cannot use any bot features.

## Monitoring

### Check Bot Logs

```bash
# View recent logs
tail -f logs/bot.log

# Search for errors
grep ERROR logs/bot.log

# Search for user actions
grep "user_id" logs/bot.log
```

### View Statistics

Use `/stats` command to see:
- Total searches
- Unique domains
- Total generations
- Total inventory files
- Total records
- Total domains
- Daily usage

## System Maintenance

### Backup Database

```bash
cp database/ulp_bot.db database/ulp_bot.db.backup
```

### Backup Inventory

```bash
cp -r inventory/ inventory.backup/
```

### Clean Old Exports

Exports older than 7 days are automatically cleaned up.

### Enable Maintenance Mode

Edit `config.json`:

```json
{
  "maintenance_mode": true
}
```

Restart the bot. Users will see a maintenance message.

## Troubleshooting

### Bot Not Responding

1. Check bot token in `config.json`
2. Check internet connection
3. Restart bot: `systemctl restart ulp-bot`
4. Check logs: `tail -f logs/bot.log`

### Inventory Not Loading

1. Verify files are in `inventory/` directory
2. Check file permissions: `chmod 644 inventory/*.txt`
3. Run `/reload` to force reload
4. Check logs for errors

### Database Errors

1. Check disk space
2. Check file permissions
3. Backup and delete `database/ulp_bot.db` to reset

### High CPU Usage

1. Check for large inventory files
2. Increase cooldown time in `config.json`
3. Check logs for errors
4. Consider splitting large inventory files

## Performance Tips

1. **Keep inventory files under 100MB** - Improves loading speed
2. **Split large datasets** - Use multiple inventory files
3. **Regular cleanup** - Remove duplicates and invalid records
4. **Monitor logs** - Look for errors early
5. **Use appropriate limits** - Don't set too high
6. **Backup regularly** - Protect against data loss

## Security Best Practices

1. **Keep bot token secret** - Never share it
2. **Use strong admin ID** - Only trusted admins
3. **Monitor logs** - Watch for suspicious activity
4. **Ban bad actors** - Remove problematic users
5. **Validate input** - The bot does this automatically
6. **Backup data** - Regular backups
7. **Use HTTPS** - If hosting on web
8. **Restrict admin access** - Only give to trusted people

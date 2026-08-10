# ULP Bot Features

## 🔍 Domain Search

- **Exact Match Search** - Find exact domain matches
- **Subdomain Matching** - Find subdomains
- **Case-Insensitive** - Search without worrying about case
- **Multi-File Search** - Search across multiple inventory files
- **Search History** - Track your search history
- **Pagination** - Handle large result sets
- **Domain Statistics** - View statistics per domain
- **Search Caching** - Fast repeated searches

## 📋 Credential Generation

- **Multiple Output Formats**:
  - `WITH_URL` - domain:login:pass
  - `WITHOUT_URL` - login:pass
  - `URL_ONLY` - domain only
  - `LOGIN_ONLY` - login only

- **Random Selection** - Randomly select credentials
- **Duplicate Protection** - Avoid duplicate credentials
- **Generation Preview** - Preview before generating
- **TXT Export** - Export to text file
- **Generation History** - Track all generations
- **Generation Statistics** - View generation stats

## 📂 Inventory Management

- **Multiple File Support** - Support for multiple TXT files
- **Auto Detection** - Automatically detect .txt files
- **Add Inventory** - Add new inventory files
- **Remove Inventory** - Remove inventory files
- **Reload Inventory** - Refresh inventory data
- **File Size Info** - View file size information
- **Record Counter** - Count total records per file
- **Last Updated** - Track when inventory was updated
- **Duplicate Detection** - Find duplicate records
- **Invalid Line Detection** - Find malformed records
- **Empty Line Cleanup** - Remove empty lines

## 🛠️ ULP Parser

- **URL Detection** - Detect URLs in various formats
- **Login Detection** - Extract login information
- **Password Detection** - Extract password information
- **Format Validation** - Validate ULP format
- **Malformed Line Detection** - Identify bad records
- **URL Normalization** - Normalize URLs to standard format
- **Record Validation** - Validate each record
- **Multiple Format Support**:
  - Standard: `URL:LOGIN:PASS`
  - HTTPS: `https://domain:login:pass`
  - Custom Scheme: `scheme://cred@domain/:login:pass`

## 🧹 Data Cleanup

- **Remove Empty Lines** - Clean up empty lines
- **Remove Duplicates** - Eliminate duplicate records
- **URL Deduplication** - Find duplicate URLs
- **Malformed Detection** - Identify bad records
- **URL Normalization** - Normalize URL format
- **Cleanup Statistics** - View cleanup results
- **Cleanup Report** - Detailed cleanup report

## 🔎 Advanced Search

- **Fast Domain Search** - Optimized search performance
- **Domain Autocomplete** - Suggest domains as you type
- **Indexed Search** - Database-backed search
- **Search Caching** - Cache search results
- **Pagination** - Handle large datasets
- **Search History** - View previous searches
- **Per-Domain Statistics** - Stats for each domain

## 📊 Statistics

- **Total Records** - Total credentials in inventory
- **Total Domains** - Unique domains tracked
- **Total Inventory Files** - Number of inventory files
- **Records Per File** - Records in each file
- **Records Per Domain** - Records for each domain
- **Largest Inventory** - Biggest file
- **Smallest Inventory** - Smallest file
- **Last Updated** - When inventory was last updated
- **Daily Statistics** - Statistics per day

## 👤 User System

- **Automatic Registration** - Users auto-register on first use
- **User Profiles** - User profile information
- **User Statistics** - Track user stats
- **Search Limits** - Daily search limits
- **Generation Limits** - Daily generation limits
- **Daily Limits** - Track daily usage
- **Cooldown System** - Rate limiting between actions
- **User History** - Track user actions
- **Block/Unblock** - Ban/unban users

## 💰 Credit System

- **User Credits** - Credit balance per user
- **Credit Balance** - View current balance
- **Credit History** - Transaction history
- **Add Credits** - Admin can add credits
- **Remove Credits** - Admin can remove credits
- **Reset Credits** - Reset user credits
- **Configurable Costs** - Set search/generation costs
- **Transaction Logs** - Log all transactions

## 📜 Generation History

- **Generation ID** - Unique ID for each generation
- **Domain** - Domain that was generated
- **Quantity** - Number of credentials generated
- **Output Format** - Format used
- **Inventory Source** - Which file was used
- **Generation Time** - When it was generated
- **User ID** - Which user generated it
- **Statistics** - Generation statistics

## 💾 Export System

- **TXT Export** - Export to text files
- **Auto Filenames** - Automatically generate filenames
- **Timestamped Files** - Include timestamp in filename
- **Result Counter** - Count exported results
- **Export Status** - View export status
- **Temp File Cleanup** - Clean up temporary files
- **Regenerate** - Re-export previous generations

## 🛡️ Admin Panel

- **Admin Dashboard** - Overview of system
- **User Management** - Manage users
- **Inventory Management** - Manage inventory files
- **Domain Statistics** - View domain stats
- **Credit Management** - Manage user credits
- **User Limits** - Set user limits
- **Ban User** - Block users
- **Unban User** - Unblock users
- **Broadcast Messages** - Send announcements
- **Maintenance Mode** - Enable maintenance
- **System Settings** - Configure bot
- **Admin Logs** - View admin actions

## 📋 Admin Inventory Tools

- **Add TXT Inventory** - Add new files
- **Remove TXT Inventory** - Remove files
- **Reload Inventory** - Refresh all files
- **Scan Inventory** - Scan for issues
- **Validate Inventory** - Validate file format
- **Clean Inventory** - Clean up file
- **Duplicate Scan** - Find duplicates
- **Domain Indexing** - Index domains
- **Inventory Statistics** - View stats
- **Inventory Status** - Check status

## 🔐 Security

- **Admin Authorization** - Restrict admin commands
- **User Authorization** - Check user permissions
- **Rate Limiting** - Prevent spam
- **Anti-Spam Protection** - Cooldown system
- **Cooldown Protection** - Time-based rate limiting
- **Input Validation** - Validate all input
- **File Size Limits** - Max file size enforcement
- **Temp File Cleanup** - Clean up temporary files
- **Error Logging** - Log all errors
- **Audit Logging** - Log all admin actions
- **Sensitive Data Protection** - Protect passwords

## 📱 Bot Commands

### User Commands
- `/start` - Start the bot
- `/help` - Show help
- `/profile` - View profile
- `/balance` - Check credits
- `/search` - Search domains
- `/domain` - Domain statistics
- `/inventory` - View inventory
- `/generate` - Generate credentials
- `/history` - View history
- `/stats` - View statistics
- `/settings` - Manage settings

### Admin Commands
- `/admin` - Admin panel
- `/users` - User management
- `/addcredits` - Add credits
- `/removecredits` - Remove credits
- `/broadcast` - Send announcement
- `/addinventory` - Add inventory
- `/removeinventory` - Remove inventory
- `/reload` - Reload inventory
- `/logs` - View logs
- `/maintenance` - Maintenance mode

## ⚙️ System Features

- **SQLite Database** - Lightweight database
- **Persistent Data** - Data survives restarts
- **Automatic Backups** - Backup functionality
- **Error Logging** - Comprehensive logging
- **Audit Trail** - Track all actions
- **Maintenance Mode** - Disable bot temporarily
- **Health Status** - Monitor system health
- **Performance Optimization** - Fast operations

#!/usr/bin/env python3
"""
Script to reload the player database with corrected clustering logic
This will clear old data and reload from CSV with the fixed rating-based clustering
"""

import sys
sys.path.insert(0, '/root/project')

from app import app, db, Player, load_players_from_csv

print("🔄 Starting database reload with corrected clustering logic...")
print("=" * 70)

with app.app_context():
    # Step 1: Clear existing players
    print("📋 Step 1: Clearing existing player data...")
    try:
        deleted_count = Player.query.delete()
        db.session.commit()
        print(f"✅ Deleted {deleted_count} existing players")
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        db.session.rollback()
        sys.exit(1)
    
    # Step 2: Reload from CSV with new logic
    print("\n📋 Step 2: Loading players from CSV with corrected rating-based clustering...")
    try:
        load_players_from_csv()
        print("✅ Players reloaded successfully")
    except Exception as e:
        print(f"❌ Error reloading CSV: {e}")
        sys.exit(1)
    
    # Step 3: Verify the clustering
    print("\n📋 Step 3: Verifying clustering distribution...")
    try:
        top_count = Player.query.filter_by(performance_label="Top Performer").count()
        avg_count = Player.query.filter_by(performance_label="Average Performer").count()
        low_count = Player.query.filter_by(performance_label="Low Performer").count()
        
        print(f"✅ Top Performers (81-100): {top_count}")
        print(f"✅ Average Performers (51-80): {avg_count}")
        print(f"✅ Low Performers (0-50): {low_count}")
        print(f"✅ Total Players: {top_count + avg_count + low_count}")
    except Exception as e:
        print(f"❌ Error verifying clusters: {e}")
        sys.exit(1)
    
    # Step 4: Show sample players from each category
    print("\n📋 Step 4: Sample players from each category...")
    try:
        print("\n⭐ Top Performers (Rating 81-100):")
        top_players = Player.query.filter_by(performance_label="Top Performer").limit(5).all()
        for p in top_players:
            print(f"  - {p.name}: Rating {p.overall_rating:.1f}, Cluster {p.cluster}, {p.performance_label}")
        
        print("\n📊 Average Performers (Rating 51-80):")
        avg_players = Player.query.filter_by(performance_label="Average Performer").limit(5).all()
        for p in avg_players:
            print(f"  - {p.name}: Rating {p.overall_rating:.1f}, Cluster {p.cluster}, {p.performance_label}")
        
        print("\n📉 Low Performers (Rating 0-50):")
        low_players = Player.query.filter_by(performance_label="Low Performer").limit(5).all()
        for p in low_players:
            print(f"  - {p.name}: Rating {p.overall_rating:.1f}, Cluster {p.cluster}, {p.performance_label}")
    except Exception as e:
        print(f"❌ Error showing samples: {e}")
        sys.exit(1)

print("\n" + "=" * 70)
print("✅ Database reload completed successfully!")
print("   The clustering logic now correctly assigns:")
print("   - 81-100 → Top Performer (Cluster 0)")
print("   - 51-80  → Average Performer (Cluster 1)")
print("   - 0-50   → Low Performer (Cluster 2)")
print("=" * 70)

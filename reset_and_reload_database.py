#!/usr/bin/env python3
"""
Database Reset and Reload Script
Clears all old position-based clustering data and reloads with rating-based logic
"""

import os
import sys

# Add the project directory to path
sys.path.insert(0, r'c:\5th sem\LABEL_DBMS')

def reset_and_reload():
    try:
        from app import app, db, Player
        from ml.clustering import predict_cluster_and_performance
        import csv
        
        with app.app_context():
            print("=" * 80)
            print("🔄 DATABASE RESET AND RELOAD WITH RATING-BASED CLUSTERING")
            print("=" * 80)
            
            # Step 1: Count and delete old data
            print("\n📋 STEP 1: Checking existing players...")
            old_count = Player.query.count()
            print(f"   Found {old_count} old players in database")
            
            if old_count > 0:
                print(f"   🗑️  Deleting {old_count} old players with position-based clustering...")
                try:
                    Player.query.delete()
                    db.session.commit()
                    print(f"   ✅ Successfully deleted all old players")
                except Exception as e:
                    print(f"   ❌ Error deleting players: {e}")
                    db.session.rollback()
                    return False
            else:
                print("   ℹ️  Database is already empty")
            
            # Step 2: Load fresh players from CSV with new clustering
            print("\n📋 STEP 2: Loading players from CSV with rating-based clustering...")
            try:
                with open(r"c:\5th sem\LABEL_DBMS\data\fifa_players_clustered_output.csv", newline="", encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    batch_size = 100
                    batch = []
                    total_loaded = 0
                    
                    for row in reader:
                        try:
                            if not row.get("overall_rating"):
                                continue
                            
                            rating = float(row.get("overall_rating", 0))
                            
                            # Get prediction based on RATING ONLY
                            prediction = predict_cluster_and_performance(rating)
                            
                            player = Player(
                                name=row.get("name", "Unknown"),
                                age=int(float(row.get("age", 0))) if row.get("age") else 0,
                                positions=row.get("positions", "Unknown"),
                                overall_rating=rating,
                                cluster=prediction['cluster'],
                                performance_label=prediction['performance_label']
                            )
                            batch.append(player)
                            total_loaded += 1
                            
                            if len(batch) >= batch_size:
                                db.session.add_all(batch)
                                db.session.commit()
                                print(f"   ✅ Loaded {total_loaded} players so far...")
                                batch = []
                        
                        except (ValueError, TypeError) as e:
                            continue
                    
                    # Commit remaining
                    if batch:
                        db.session.add_all(batch)
                        db.session.commit()
                    
                    print(f"   ✅ Successfully loaded {total_loaded} players from CSV")
                
            except Exception as e:
                print(f"   ❌ Error loading CSV: {e}")
                db.session.rollback()
                return False
            
            # Step 3: Verify clustering distribution
            print("\n📋 STEP 3: Verifying clustering distribution...")
            try:
                top_count = Player.query.filter_by(performance_label="Top Performer").count()
                avg_count = Player.query.filter_by(performance_label="Average Performer").count()
                low_count = Player.query.filter_by(performance_label="Low Performer").count()
                total = Player.query.count()
                
                print(f"\n   📊 CLUSTERING DISTRIBUTION:")
                print(f"   ⭐ Top Performers (Rating 81-100, Cluster 0):    {top_count:5d} players")
                print(f"   📊 Average Performers (Rating 51-80, Cluster 1): {avg_count:5d} players")
                print(f"   📉 Low Performers (Rating 0-50, Cluster 2):      {low_count:5d} players")
                print(f"   {'─' * 60}")
                print(f"   Total:                                            {total:5d} players")
            
            except Exception as e:
                print(f"   ❌ Error verifying clusters: {e}")
                return False
            
            # Step 4: Show sample players from each position
            print("\n📋 STEP 4: Sample verification - checking all positions are clustering by RATING only...\n")
            
            positions_to_check = ['CF', 'RW', 'ST', 'CAM', 'RM', 'CM', 'LW', 'CDM', 'LB', 'GK', 'CB']
            
            for position in positions_to_check:
                try:
                    # Get top performer in this position
                    top_in_pos = Player.query.filter(
                        Player.positions.like(f'%{position}%'),
                        Player.performance_label == "Top Performer"
                    ).first()
                    
                    avg_in_pos = Player.query.filter(
                        Player.positions.like(f'%{position}%'),
                        Player.performance_label == "Average Performer"
                    ).first()
                    
                    low_in_pos = Player.query.filter(
                        Player.positions.like(f'%{position}%'),
                        Player.performance_label == "Low Performer"
                    ).first()
                    
                    print(f"   {position}:")
                    if top_in_pos:
                        print(f"      ⭐ Top:     {top_in_pos.name} (Rating {top_in_pos.overall_rating:.1f}) → Cluster {top_in_pos.cluster}")
                    if avg_in_pos:
                        print(f"      📊 Avg:     {avg_in_pos.name} (Rating {avg_in_pos.overall_rating:.1f}) → Cluster {avg_in_pos.cluster}")
                    if low_in_pos:
                        print(f"      📉 Low:     {low_in_pos.name} (Rating {low_in_pos.overall_rating:.1f}) → Cluster {low_in_pos.cluster}")
                    print()
                
                except Exception as e:
                    print(f"   ⚠️  Error checking {position}: {e}\n")
            
            print("=" * 80)
            print("✅ DATABASE RELOAD COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print("\n📌 KEY POINTS:")
            print("   ✅ All position-based clustering REMOVED")
            print("   ✅ Clustering is now PURELY RATING-BASED")
            print("   ✅ All positions (CF, RW, ST, CAM, RM, CM, LW, CDM, LB, GK, CB)")
            print("      are now distributed across Top/Average/Low based on rating")
            print("   ✅ Top Performers:     Rating 81-100 (Cluster 0)")
            print("   ✅ Average Performers: Rating 51-80  (Cluster 1)")
            print("   ✅ Low Performers:     Rating 0-50   (Cluster 2)")
            print("\n🔗 Next step: Go to http://localhost:5000/players and test the filters!")
            print("=" * 80)
            
            return True
    
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure you're running this from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = reset_and_reload()
    sys.exit(0 if success else 1)

from app import create_app, db
from app.models import User
from datetime import datetime

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tables created")

    # Admin
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@buildsa.co.za',
            full_name='BuildSA Administrator',
            phone_number='+27818795563',
            city='Pretoria',
            province='Gauteng',
            profession='Administrator',
            is_admin=True,
            is_active=True,
            is_verified=True,
            is_verified_builder=True,
            approved_at=datetime.utcnow(),
        )
        admin.set_password('Admin@2024!')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created: admin / Admin@2024!")
    else:
        print("ℹ️  Admin already exists")

    # Demo builder (so you can test posts/messages)
    demo = User.query.filter_by(username='builder1').first()
    if not demo:
        demo = User(
            username='builder1',
            email='builder1@buildsa.co.za',
            full_name='Sipho Nkosi',
            phone_number='+27821234567',
            city='Johannesburg',
            province='Gauteng',
            profession='Builder',
            bio='15 years experience in residential building.',
            is_admin=False,
            is_active=True,
            is_verified=True,
            is_verified_builder=True,
            approved_at=datetime.utcnow(),
        )
        demo.set_password('Builder@2024!')
        db.session.add(demo)
        db.session.commit()
        print("✅ Demo builder created: builder1 / Builder@2024!")

    print("✅ Database initialization complete!")

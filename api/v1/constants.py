# apps/classified/constants.py

class JobStatus:
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

    CHOICES = [
        (PENDING, "Pending"),
        (ASSIGNED, "Assigned"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

class JobOfferStatus:
    NEW = "New"
    NEGOTIATING = "Negotiating"
    PROVIDER_ACCEPTED = "Provider Accepted"
    CUSTOMER_ACCEPTED = "Customer Accepted"
    REJECTED = "Rejected"

    CHOICES = [
        (NEW, "New"),
        (NEGOTIATING, "Negotiating"),
        (PROVIDER_ACCEPTED, "Provider Accepted"),
        (CUSTOMER_ACCEPTED, "Customer Accepted"),
        (REJECTED, "Rejected"),
    ]

class JobProgressStatus:
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

    CHOICES = [
        (PENDING, "Pending"),
        (ASSIGNED, "Assigned"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

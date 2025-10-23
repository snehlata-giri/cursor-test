from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.vendor import Vendor
from app.models.vendor_service import VendorService
from app.models.service_pricing import ServicePricing
from app.models.vendor_location import VendorLocation

router = APIRouter()

@router.get("/vendors")
async def get_vendors(db: AsyncSession = Depends(get_db)):
    """Get all vendors with their basic information"""
    try:
        result = await db.execute(select(Vendor))
        vendors = result.scalars().all()
        
        return [
            {
                "id": vendor.id,
                "name": vendor.name,
                "email": vendor.email,
                "phone": vendor.phone,
                "website": vendor.website,
                "rating": float(vendor.rating) if vendor.rating else 0.0,
                "established_year": vendor.established_year,
                "description": vendor.description
            }
            for vendor in vendors
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services")
async def get_services(db: AsyncSession = Depends(get_db)):
    """Get all services with vendor information"""
    try:
        result = await db.execute(
            select(VendorService, Vendor.name.label('vendor_name'))
            .join(Vendor, VendorService.vendor_id == Vendor.id)
        )
        services = result.all()
        
        return [
            {
                "id": service.VendorService.id,
                "vendor_id": service.VendorService.vendor_id,
                "service_name": service.VendorService.service_name,
                "category": service.VendorService.category,
                "description": service.VendorService.description,
                "is_active": service.VendorService.is_active,
                "vendor_name": service.vendor_name
            }
            for service in services
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pricing")
async def get_pricing(db: AsyncSession = Depends(get_db)):
    """Get all pricing information with service and vendor details"""
    try:
        result = await db.execute(
            select(ServicePricing, VendorService.service_name, Vendor.name.label('vendor_name'))
            .join(VendorService, ServicePricing.vendor_service_id == VendorService.id)
            .join(Vendor, VendorService.vendor_id == Vendor.id)
        )
        pricing_data = result.all()
        
        return [
            {
                "id": price.ServicePricing.id,
                "vendor_service_id": price.ServicePricing.vendor_service_id,
                "pricing_type": price.ServicePricing.pricing_type,
                "base_price": float(price.ServicePricing.base_price),
                "currency": price.ServicePricing.currency,
                "unit": price.ServicePricing.unit,
                "discount_percentage": float(price.ServicePricing.discount_percentage),
                "is_active": price.ServicePricing.is_active,
                "service_name": price.service_name,
                "vendor_name": price.vendor_name
            }
            for price in pricing_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



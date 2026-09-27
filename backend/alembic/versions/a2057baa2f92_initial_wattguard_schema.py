"""Initial WattGuard schema

Revision ID: a2057baa2f92
Revises: 
Create Date: 2026-09-26 15:16:46.787260

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a2057baa2f92'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Consumers table
    op.create_table(
        'consumers',
        sa.Column('consumer_id', sa.String(length=64), primary_key=True),
        sa.Column('sanctioned_load_kw', sa.Float(), nullable=False),
        sa.Column('tariff_class', sa.String(length=32), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('feeder_id', sa.String(length=32), nullable=False),
        sa.Column('transformer_id', sa.String(length=32), nullable=False),
        sa.Column('phase', sa.String(length=8), nullable=False),
        sa.Column('has_solar', sa.Boolean(), default=False),
        sa.Column('safety_hazard_flag', sa.Boolean(), default=False),
        sa.Column('security_escort_required', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_consumers_consumer_id', 'consumers', ['consumer_id'])
    op.create_index('ix_consumers_tariff_class', 'consumers', ['tariff_class'])
    op.create_index('ix_consumers_feeder_id', 'consumers', ['feeder_id'])
    op.create_index('ix_consumers_transformer_id', 'consumers', ['transformer_id'])

    # 2. Meter Readings table
    op.create_table(
        'meter_readings',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('consumer_id', sa.String(length=64), sa.ForeignKey('consumers.consumer_id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('energy_kwh', sa.Float(), nullable=False),
        sa.Column('submeter_hvac_kwh', sa.Float(), default=0.0),
        sa.Column('submeter_lighting_kwh', sa.Float(), default=0.0),
        sa.Column('tamper_flags', sa.String(length=64), default='NORMAL'),
        sa.Column('is_theft_ground_truth', sa.Boolean(), default=False),
        sa.Column('theft_type', sa.String(length=32), default='Normal')
    )
    op.create_index('ix_meter_readings_consumer_id', 'meter_readings', ['consumer_id'])
    op.create_index('ix_meter_readings_timestamp', 'meter_readings', ['timestamp'])

    # 3. Alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('alert_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('consumer_id', sa.String(length=64), sa.ForeignKey('consumers.consumer_id', ondelete='CASCADE'), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('anomaly_score', sa.Float(), nullable=False),
        sa.Column('feeder_loss_factor', sa.Float(), default=0.0),
        sa.Column('composite_priority', sa.Float(), nullable=False),
        sa.Column('risk_tier', sa.String(length=16), nullable=False),
        sa.Column('estimated_unbilled_kwh', sa.Float(), default=0.0),
        sa.Column('estimated_loss_currency', sa.Float(), default=0.0),
        sa.Column('loss_lower_bound_95', sa.Float(), default=0.0),
        sa.Column('loss_upper_bound_95', sa.Float(), default=0.0),
        sa.Column('net_roi_yield', sa.Float(), default=0.0),
        sa.Column('recommended_action', sa.String(length=64), nullable=False),
        sa.Column('security_escort_required', sa.Boolean(), default=False),
        sa.Column('plain_language_explanation', sa.Text(), nullable=True),
        sa.Column('shap_feature_importance', sa.Text(), nullable=True),
        sa.Column('hardware_tamper_evidence', sa.String(length=128), default='NORMAL'),
        sa.Column('status', sa.String(length=32), default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_alerts_alert_id', 'alerts', ['alert_id'])
    op.create_index('ix_alerts_consumer_id', 'alerts', ['consumer_id'])

    # 4. Inspections table
    op.create_table(
        'inspections',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('inspection_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('alert_id', sa.String(length=64), sa.ForeignKey('alerts.alert_id', ondelete='SET NULL'), nullable=True),
        sa.Column('consumer_id', sa.String(length=64), sa.ForeignKey('consumers.consumer_id', ondelete='CASCADE'), nullable=False),
        sa.Column('inspector_id', sa.String(length=64), nullable=False),
        sa.Column('audit_status', sa.String(length=64), nullable=False),
        sa.Column('meter_serial', sa.String(length=64), nullable=False),
        sa.Column('seal_number', sa.String(length=64), nullable=False),
        sa.Column('observed_load', sa.Float(), default=0.0),
        sa.Column('inspector_notes', sa.Text(), nullable=True),
        sa.Column('photo_evidence_paths', sa.Text(), default='[]'),
        sa.Column('photo_metadata', sa.Text(), default='[]'),
        sa.Column('inspection_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_inspections_inspection_id', 'inspections', ['inspection_id'])
    op.create_index('ix_inspections_consumer_id', 'inspections', ['consumer_id'])
    op.create_index('ix_inspections_alert_id', 'inspections', ['alert_id'])

    # 5. Whistleblower Tips table
    op.create_table(
        'whistleblower_tips',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('tip_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('approximate_address', sa.String(length=256), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('transformer_hint', sa.String(length=64), nullable=True),
        sa.Column('correlated_consumer_ids', sa.Text(), default='[]'),
        sa.Column('status', sa.String(length=32), default='PENDING_REVIEW'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_whistleblower_tips_tip_id', 'whistleblower_tips', ['tip_id'])


def downgrade() -> None:
    op.drop_table('whistleblower_tips')
    op.drop_table('inspections')
    op.drop_table('alerts')
    op.drop_table('meter_readings')
    op.drop_table('consumers')
